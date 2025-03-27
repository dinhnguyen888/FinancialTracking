using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows.Input;
using PersonalFinanceManagement.Models;

namespace PersonalFinanceManagement.ViewModels.Dialogs
{
    public class TransactionDialogViewModel : ViewModelBase, IDataErrorInfo
    {
        private readonly bool _isIncome;
        private string _dialogTitle;
        private decimal _amount;
        private DateTime _date;
        private string _description;
        private Category? _selectedCategory;
        private string _source;
        private bool _isEssential;
        private string _selectedPaymentMethod;
        private List<Category> _categories;
        private List<string> _paymentMethods;
        private bool _isSaving;

        public TransactionDialogViewModel(bool isIncome, Transaction? transaction = null)
        {
            _isIncome = isIncome;
            _dialogTitle = isIncome ? "Thu Nhập" : "Chi Tiêu";
            _dialogTitle = transaction == null ? $"Thêm {_dialogTitle}" : $"Sửa {_dialogTitle}";
            
            _date = transaction?.Date ?? DateTime.Now;
            _amount = transaction?.Amount ?? 0;
            _description = transaction?.Description ?? string.Empty;
            _selectedCategory = transaction?.Category;
            
            if (isIncome && transaction is Income income)
            {
                _source = income.Source;
            }
            else if (!isIncome && transaction is Expense expense)
            {
                _isEssential = expense.IsEssential;
                _selectedPaymentMethod = expense.PaymentMethod;
            }

            _categories = new List<Category>();
            _paymentMethods = new List<string>
            {
                "Tiền Mặt",
                "Thẻ Tín Dụng",
                "Thẻ Ghi Nợ",
                "Chuyển Khoản",
                "Ví Điện Tử"
            };

            SaveCommand = new RelayCommand(_ => Save(), _ => CanSave());
            CancelCommand = new RelayCommand(_ => Cancel());
        }

        #region Properties

        public string DialogTitle
        {
            get => _dialogTitle;
            set => SetProperty(ref _dialogTitle, value);
        }

        public decimal Amount
        {
            get => _amount;
            set => SetProperty(ref _amount, value);
        }

        public DateTime Date
        {
            get => _date;
            set => SetProperty(ref _date, value);
        }

        public string Description
        {
            get => _description;
            set => SetProperty(ref _description, value);
        }

        public Category? SelectedCategory
        {
            get => _selectedCategory;
            set => SetProperty(ref _selectedCategory, value);
        }

        public List<Category> Categories
        {
            get => _categories;
            set => SetProperty(ref _categories, value);
        }

        public string Source
        {
            get => _source;
            set => SetProperty(ref _source, value);
        }

        public bool IsEssential
        {
            get => _isEssential;
            set => SetProperty(ref _isEssential, value);
        }

        public string SelectedPaymentMethod
        {
            get => _selectedPaymentMethod;
            set => SetProperty(ref _selectedPaymentMethod, value);
        }

        public List<string> PaymentMethods
        {
            get => _paymentMethods;
            set => SetProperty(ref _paymentMethods, value);
        }

        public bool IsIncome => _isIncome;
        public bool IsExpense => !_isIncome;

        #endregion

        #region Commands

        public ICommand SaveCommand { get; }
        public ICommand CancelCommand { get; }

        #endregion

        #region Events

        public event EventHandler? DialogClosed;
        public Transaction? Result { get; private set; }

        #endregion

        #region IDataErrorInfo Implementation

        public string Error => string.Empty;

        public string this[string columnName]
        {
            get
            {
                return columnName switch
                {
                    nameof(Amount) => ValidateAmount(),
                    nameof(Date) => ValidateDate(),
                    nameof(SelectedCategory) => ValidateCategory(),
                    _ => string.Empty
                };
            }
        }

        private string ValidateAmount()
        {
            if (Amount <= 0)
            {
                return "Số tiền phải lớn hơn 0";
            }
            return string.Empty;
        }

        private string ValidateDate()
        {
            if (Date > DateTime.Now)
            {
                return "Ngày không thể là ngày trong tương lai";
            }
            return string.Empty;
        }

        private string ValidateCategory()
        {
            if (SelectedCategory == null)
            {
                return "Vui lòng chọn danh mục";
            }
            return string.Empty;
        }

        #endregion

        #region Methods

        private bool CanSave()
        {
            if (_isSaving) return false;
            if (Amount <= 0) return false;
            if (SelectedCategory == null) return false;
            if (Date > DateTime.Now) return false;
            return true;
        }

        private void Save()
        {
            if (_isSaving) return;
            _isSaving = true;

            try
            {
                if (IsIncome)
                {
                    Result = new Income
                    {
                        Amount = Amount,
                        Date = Date,
                        Description = Description,
                        CategoryId = SelectedCategory!.Id,
                        Category = SelectedCategory,
                        Source = Source
                    };
                }
                else
                {
                    Result = new Expense
                    {
                        Amount = Amount,
                        Date = Date,
                        Description = Description,
                        CategoryId = SelectedCategory!.Id,
                        Category = SelectedCategory,
                        IsEssential = IsEssential,
                        PaymentMethod = SelectedPaymentMethod
                    };
                }

                DialogClosed?.Invoke(this, EventArgs.Empty);
            }
            finally
            {
                _isSaving = false;
            }
        }

        private void Cancel()
        {
            Result = null;
            DialogClosed?.Invoke(this, EventArgs.Empty);
        }

        public void SetCategories(IEnumerable<Category> categories)
        {
            Categories = new List<Category>(categories);
            if (SelectedCategory != null)
            {
                SelectedCategory = Categories.Find(c => c.Id == SelectedCategory.Id);
            }
        }

        #endregion
    }
}