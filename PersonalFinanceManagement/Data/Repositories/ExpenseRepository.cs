using Dapper;
using PersonalFinanceManagement.Models;
using System.Threading.Tasks;

namespace PersonalFinanceManagement.Data.Repositories
{
    public interface IExpenseRepository : IRepository<Expense>
    {
        Task<decimal> GetTotalForMonthAsync(int year, int month);
        Task<decimal> GetTotalByCategory(int categoryId);
    }

    public class ExpenseRepository : TransactionRepository<Expense>, IExpenseRepository
    {
        public ExpenseRepository(IDatabaseContext context) : base(context, "Expenses")
        {
        }

        public override async Task<int> AddAsync(Expense expense)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                INSERT INTO Expenses (Amount, Date, Description, CategoryId, IsEssential, PaymentMethod)
                VALUES (@Amount, @Date, @Description, @CategoryId, @IsEssential, @PaymentMethod);
                SELECT last_insert_rowid();";

            return await connection.QuerySingleAsync<int>(sql, new
            {
                expense.Amount,
                Date = expense.Date.ToString("yyyy-MM-dd"),
                expense.Description,
                expense.CategoryId,
                IsEssential = expense.IsEssential ? 1 : 0,
                expense.PaymentMethod
            });
        }

        public override async Task<bool> UpdateAsync(Expense expense)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                UPDATE Expenses 
                SET Amount = @Amount,
                    Date = @Date,
                    Description = @Description,
                    CategoryId = @CategoryId,
                    IsEssential = @IsEssential,
                    PaymentMethod = @PaymentMethod
                WHERE Id = @Id";

            var affected = await connection.ExecuteAsync(sql, new
            {
                expense.Id,
                expense.Amount,
                Date = expense.Date.ToString("yyyy-MM-dd"),
                expense.Description,
                expense.CategoryId,
                IsEssential = expense.IsEssential ? 1 : 0,
                expense.PaymentMethod
            });

            return affected > 0;
        }

        public async Task<decimal> GetTotalForMonthAsync(int year, int month)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                SELECT COALESCE(SUM(Amount), 0)
                FROM Expenses
                WHERE strftime('%Y', Date) = @Year 
                AND strftime('%m', Date) = @Month";

            return await connection.QuerySingleAsync<decimal>(sql, new 
            { 
                Year = year.ToString(), 
                Month = month.ToString("D2") 
            });
        }

        public async Task<decimal> GetTotalByCategory(int categoryId)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                SELECT COALESCE(SUM(Amount), 0)
                FROM Expenses
                WHERE CategoryId = @CategoryId";

            return await connection.QuerySingleAsync<decimal>(sql, new { CategoryId = categoryId });
        }
    }
}