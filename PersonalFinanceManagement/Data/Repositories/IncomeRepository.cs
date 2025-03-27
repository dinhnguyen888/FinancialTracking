using Dapper;
using PersonalFinanceManagement.Models;
using System.Threading.Tasks;

namespace PersonalFinanceManagement.Data.Repositories
{
    public interface IIncomeRepository : IRepository<Income>
    {
        Task<decimal> GetTotalForMonthAsync(int year, int month);
    }

    public class IncomeRepository : TransactionRepository<Income>, IIncomeRepository
    {
        public IncomeRepository(IDatabaseContext context) : base(context, "Incomes")
        {
        }

        public override async Task<int> AddAsync(Income income)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                INSERT INTO Incomes (Amount, Date, Description, CategoryId, Source)
                VALUES (@Amount, @Date, @Description, @CategoryId, @Source);
                SELECT last_insert_rowid();";

            return await connection.QuerySingleAsync<int>(sql, new
            {
                income.Amount,
                Date = income.Date.ToString("yyyy-MM-dd"),
                income.Description,
                income.CategoryId,
                income.Source
            });
        }

        public override async Task<bool> UpdateAsync(Income income)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                UPDATE Incomes 
                SET Amount = @Amount,
                    Date = @Date,
                    Description = @Description,
                    CategoryId = @CategoryId,
                    Source = @Source
                WHERE Id = @Id";

            var affected = await connection.ExecuteAsync(sql, new
            {
                income.Id,
                income.Amount,
                Date = income.Date.ToString("yyyy-MM-dd"),
                income.Description,
                income.CategoryId,
                income.Source
            });

            return affected > 0;
        }

        public async Task<decimal> GetTotalForMonthAsync(int year, int month)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                SELECT COALESCE(SUM(Amount), 0)
                FROM Incomes
                WHERE strftime('%Y', Date) = @Year 
                AND strftime('%m', Date) = @Month";

            return await connection.QuerySingleAsync<decimal>(sql, new 
            { 
                Year = year.ToString(), 
                Month = month.ToString("D2") 
            });
        }
    }
}