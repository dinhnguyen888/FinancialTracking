using System;

namespace PersonalFinanceManagement.Models
{
    public abstract class Transaction
    {
        public int Id { get; set; }
        public decimal Amount { get; set; }
        public DateTime Date { get; set; }
        public string Description { get; set; } = string.Empty;
        public int CategoryId { get; set; }
        public Category? Category { get; set; }
    }

    public class Income : Transaction
    {
        public string Source { get; set; } = string.Empty;
    }

    public class Expense : Transaction
    {
        public bool IsEssential { get; set; }
        public string PaymentMethod { get; set; } = string.Empty;
    }
}