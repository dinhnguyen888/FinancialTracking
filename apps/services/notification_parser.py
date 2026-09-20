import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from apps.models.notification import ParseResult

# Keyword dictionaries for smart category suggestion
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Ăn uống": [
        "coffee", "cafe", "cf", "highlands", "phuc long", "starbucks", "the coffee house",
        "an uong", "an toi", "an trua", "an sang", "com", "tra sua", "food", "shopeefood",
        "grabfood", "baemin", "buffet", "nha hang", "quan an", "pho", "banh mi",
        "winmart", "bach hoa xanh", "coopmart", "lotte mart", "kfc", "lotteria", "pizza"
    ],
    "Đi lại": [
        "grab", "be ", "be,", "xanh sm", "taxi", "mai linh", "vinataxi",
        "xang", "petrolimex", "pvoil", "gui xe", "ve xe", "ve tau", "may bay",
        "vietnam airlines", "vietjet", "bamboo", "toll", "bot", "epass", "vetc"
    ],
    "Hóa đơn & Tiện ích": [
        "dien", "evn", "nuoc", "cap nuoc", "internet", "viettel", "mobifone",
        "vinaphone", "fpt", "truyen hinh", "dien thoai", "hoa don", "cuoc", "nap tien dt"
    ],
    "Mua sắm": [
        "shopee", "lazada", "tiki", "tiktok shop", "sieu thi", "dien may",
        "the gioi di dong", "tgdd", "dien may xanh", "fpt shop", "cellphones",
        "quan ao", "zara", "uniqlo", "routine", "coolmate", "my pham"
    ],
    "Giải trí": [
        "cinema", "cgv", "lotte cinema", "bhd", "galaxy", "netflix", "spotify",
        "youtube", "game", "steam", "garena", "du lich", "khach san", "resort",
        "booking", "agoda", "karaoke", "bar", "pub"
    ],
    "Sức khỏe": [
        "thuoc", "nha thuoc", "pharmacity", "long chau", "an khang", "benh vien",
        "phong kham", "bac si", "kham benh", "gym", "fitness", "yoga", "boi loi"
    ],
    "Giáo dục": [
        "hoc phi", "khoa hoc", "sach", "fahasa", "nha sach", "tieng anh",
        "ielts", "toeic", "dai hoc", "truong hoc", "udemy", "coursera"
    ],
    "Lương": [
        "luong", "salary", "payroll", "thanh toan luong", "thu nhap", "chuyen luong"
    ],
    "Thưởng": [
        "thuong", "bonus", "kpi", "thuong nong", "khen thuong", "qua tet"
    ],
    "Đầu tư": [
        "co phieu", "chung khoan", "tiet kiem", "lai suat", "lai tk", "vps",
        "ssi", "tcbs", "vndirect", "crypto", "binance", "vang"
    ]
}

class BankNotificationParser:
    """
    Intelligent parser for Vietnamese bank & e-wallet notifications.
    Supports Vietcombank, MB Bank, Techcombank, TPBank, VPBank, ACB, BIDV, MoMo, ZaloPay, etc.
    """

    KNOWN_BANKS = [
        ("vietcombank", "Vietcombank"),
        ("vcb", "Vietcombank"),
        ("sacombank", "Sacombank"),
        ("cake", "Cake Bank"),
        ("mbbank", "MB Bank"),
        ("mb bank", "MB Bank"),
        ("techcombank", "Techcombank"),
        ("tcb", "Techcombank"),
        ("tpbank", "TPBank"),
        ("tpb", "TPBank"),
        ("vpbank", "VPBank"),
        ("acb", "ACB"),
        ("bidv", "BIDV"),
        ("agribank", "Agribank"),
        ("momo", "MoMo"),
        ("zalopay", "ZaloPay"),
        ("shopeepay", "ShopeePay"),
        ("viettel money", "Viettel Money"),
    ]

    @classmethod
    def detect_bank_name(cls, text: str, sender_app: str = "") -> str:
        combined = f"{sender_app} {text}".lower()
        for key, name in cls.KNOWN_BANKS:
            if key in combined:
                return name
        return sender_app.strip() if sender_app.strip() else "Ngân hàng"

    @classmethod
    def extract_amount_and_type(cls, text: str) -> Tuple[float, str]:
        """
        Extract transaction amount and determine if it's income (+) or expense (-).
        Handles Sacombank email/app (Phát sinh/Transaction: +/-...), Cake Bank, MoMo, etc.
        """
        lower_text = text.lower()
        
        # 1. Bilingual Email / Sacombank table format:
        # e.g. "Phát sinh/ Transaction: - 50,000 VND" or "Phát sinh/Transaction: + 100,000 VND" or "PS: +3,500,000 VND"
        bilingual_ps = re.search(r'(?:Phát sinh|Transaction|PS)[^:\n]*:\s*([+\-])\s*([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?', text, re.IGNORECASE)
        if bilingual_ps:
            sign = bilingual_ps.group(1)
            raw_amt = bilingual_ps.group(2)
            amount = cls._clean_number(raw_amt)
            tx_type = "income" if sign == "+" else "expense"
            if amount > 0:
                return amount, tx_type

        # 2. Cake Bank pattern: "vừa tăng 20.000 đ" or "vừa giảm 50.000 đ"
        cake_inc = re.search(r'vừa\s+tăng\s+([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?', text, re.IGNORECASE)
        if cake_inc:
            amount = cls._clean_number(cake_inc.group(1))
            if amount > 0:
                return amount, "income"

        cake_dec = re.search(r'vừa\s+giảm\s+([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?', text, re.IGNORECASE)
        if cake_dec:
            amount = cls._clean_number(cake_dec.group(1))
            if amount > 0:
                return amount, "expense"

        # 3. Explicit +/- sign with amount: e.g. "+150,000", "-50.000", "+ 2,000,000 VND"
        sign_match = re.search(r'([+\-])\s*([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?', text, re.IGNORECASE)
        if sign_match:
            sign = sign_match.group(1)
            raw_amt = sign_match.group(2)
            amount = cls._clean_number(raw_amt)
            tx_type = "income" if sign == "+" else "expense"
            if amount > 0:
                return amount, tx_type

        # 4. Check income keywords vs expense keywords
        is_income = any(k in lower_text for k in [
            "nhan duoc", "nhận được", "nhan tien", "nhận tiền", "cộng", "cong vao",
            "hoan tien", "hoàn tiền", "nap tien vao", "nạp tiền vào", "tien vao",
            "tiền vào", "lai tiet kiem", "vua tang", "vừa tăng"
        ])

        is_expense = any(k in lower_text for k in [
            "thanh toan", "thanh toán", "chuyen tien", "chuyển tiền", "chuyen khoan",
            "tru tien", "trừ tiền", "rut tien", "rút tiền", "phi duy tri", "giao dich", "gd:"
        ])

        # 5. MoMo / General: "Số tiền: 20.000 đ" or "Số tiền 20.000 đ"
        amt_labeled_match = re.search(r'(?:Số tiền|so tien)\s*:?\s*([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?', text, re.IGNORECASE)
        if amt_labeled_match:
            raw_amt = amt_labeled_match.group(1)
            amount = cls._clean_number(raw_amt)
            if amount > 0:
                tx_type = "income" if is_income else "expense"
                return amount, tx_type

        # 6. Match generic number pattern followed by VND/đ
        amt_match = re.search(r'([\d\.,]{3,})\s*(?:vnd|vnđ|d|đ)\b', text, re.IGNORECASE)
        if amt_match:
            raw_amt = amt_match.group(1)
            amount = cls._clean_number(raw_amt)
            if amount > 0:
                tx_type = "income" if is_income and not is_expense else "expense"
                return amount, tx_type

        # 7. Fallback search for any 4+ digit number
        all_numbers = re.findall(r'\b\d{1,3}(?:[\.,]\d{3})+\b', text)
        if all_numbers:
            amount = cls._clean_number(all_numbers[0])
            tx_type = "income" if is_income else "expense"
            return amount, tx_type

        return 0.0, "expense"

    @classmethod
    def extract_description(cls, text: str) -> str:
        """
        Extract transaction description (Nội dung/Description, ND, Ref, kèm lời nhắn, etc.)
        """
        # 1. Sacombank Email / Bilingual template: "Nội dung/ Description: ..."
        email_desc = re.search(r'(?:Nội dung|Description)[^:\n]*:\s*([^\r\n]+)', text, re.IGNORECASE)
        if email_desc:
            desc = email_desc.group(1).strip().strip('"').strip("'").strip('“').strip('”')
            if len(desc) >= 3:
                return desc

        # 2. Sacombank Pay tail: text after 'Số dư khả dụng: ... VND.'
        saco_match = re.search(r'Số dư khả dụng:[^.]*\.\s*(.+)', text, re.IGNORECASE)
        if saco_match:
            desc = saco_match.group(1).strip()
            if len(desc) >= 3:
                return desc

        # 3. Explicit label markers
        priority_patterns = [
            r'(?:kèm lời nhắn|lời nhắn|loi nhan):\s*["“]?([^"”\n\.]+)',
            r'(?:ND|Noi dung|Ghi chu|Ghi chú):\s*([^.\n]+)',
            r'(?:tai|tại|cho)\s+([A-Z0-9\s&_\-]+?)(?:qua|\.|$)',
            r'(?:GD|Ref):\s*([^.\n]+)',
        ]
        for pat in priority_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                desc = match.group(1).strip().strip('"').strip("'").strip('“').strip('”')
                if len(desc) >= 3:
                    return desc
        
        # 4. If no explicit marker, use cleaned short preview
        cleaned = re.sub(r'[\r\n]+', ' ', text).strip()
        if len(cleaned) > 50:
            return cleaned[:47] + "..."
        return cleaned

    @classmethod
    def suggest_category(cls, description: str, raw_text: str, tx_type: str) -> str:
        # Match primarily on description with word boundaries to avoid false positives (e.g. 'com' in sacombank.com)
        desc_lower = description.lower()
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                pattern = r'(?<![a-zA-Z0-9_])' + re.escape(kw.lower()) + r'(?![a-zA-Z0-9_])'
                if re.search(pattern, desc_lower):
                    return category

        return "Thu nhập khác" if tx_type == "income" else "Chi tiêu khác"

    @classmethod
    def parse(cls, raw_message: str, sender_app: str = "") -> ParseResult:
        if not raw_message or not raw_message.strip():
            return ParseResult(is_valid=False)

        bank_name = cls.detect_bank_name(raw_message, sender_app)
        amount, tx_type = cls.extract_amount_and_type(raw_message)

        if amount <= 0:
            return ParseResult(
                is_valid=False,
                bank_name=bank_name,
                raw_message=raw_message
            )

        description = cls.extract_description(raw_message)
        suggested_cat = cls.suggest_category(description, raw_message, tx_type)

        # Extract balance if present:
        # Handles "Số dư khả dụng/ Available balance: 19,909,423 VND" (Sacombank email)
        # Handles "Số dư khả dụng: 19,957,923 VND" (Sacombank app)
        # Handles "Số dư hiện tại của tài khoản thanh toán là 66.428 đ" (Cake Bank)
        balance = None
        bal_patterns = [
            r'(?:Số dư khả dụng|Available balance|Số dư|Balance|SD cuoi|So du)[^:\n]*:\s*([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?',
            r'Số dư hiện tại[^:]*là\s*([\d\.,]+)\s*(?:vnd|vnđ|d|đ)?',
        ]
        for b_pat in bal_patterns:
            bal_match = re.search(b_pat, raw_message, re.IGNORECASE)
            if bal_match:
                balance = cls._clean_number(bal_match.group(1))
                break

        # Extract transaction date/time if present in email/message
        # e.g. "Ngày/ Date: 20/09/2026 20:37"
        tx_time = None
        date_match = re.search(r'(?:Ngày|Date)[^:\n]*:\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{4}(?:\s+[0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?)?)', raw_message, re.IGNORECASE)
        if date_match:
            raw_date_str = date_match.group(1).strip()
            for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    dt = datetime.strptime(raw_date_str, fmt)
                    tx_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    break
                except Exception:
                    pass
        if not tx_time:
            tx_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return ParseResult(
            is_valid=True,
            bank_name=bank_name,
            amount=amount,
            transaction_type=tx_type,
            description=description,
            suggested_category=suggested_cat,
            balance=balance,
            transaction_time=tx_time,
            raw_message=raw_message
        )

    @staticmethod
    def _clean_number(num_str: str) -> float:
        try:
            cleaned = num_str.strip()
            # If string contains both '.' and ',' (e.g. 1.250.000,50 or 1,250,000.50)
            if '.' in cleaned and ',' in cleaned:
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    # Vietnamese / European: 1.250.000,50
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # US: 1,250,000.50
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Could be 150,000 (thousand sep) or 15,5 (decimal)
                parts = cleaned.split(',')
                if all(len(p) == 3 for p in parts[1:]):
                    cleaned = cleaned.replace(',', '')
                else:
                    cleaned = cleaned.replace(',', '.')
            elif '.' in cleaned:
                # Could be 150.000 (Vietnamese thousand sep) or 15.5
                parts = cleaned.split('.')
                if all(len(p) == 3 for p in parts[1:]):
                    cleaned = cleaned.replace('.', '')

            return float(cleaned)
        except Exception:
            return 0.0
