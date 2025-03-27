using Dapper;
using PersonalFinanceManagement.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace PersonalFinanceManagement.Data.Repositories
{
    public abstract class TransactionRepository<T> : IRepository<T> where T : Transaction
    {
        protected readonly IDatabaseContext _context;
        protected readonly string _tableName;

        protected TransactionRepository(IDatabaseContext context, string tableName)
        {
            _context = context;
            _tableName = tableName;
        }

        public virtual async Task<IEnumerable<T>> GetAllAsync()
        {
            using var connection = _context.CreateConnection();
            var sql = $@"
                SELECT t.*, c.* 
                FROM {_tableName} t
                LEFT JOIN Categories c ON t.CategoryId = c.Id
                ORDER BY t.Date DESC";
            
            var transactions = await connection.QueryAsync<T, Category, T>(
                sql,
                (transaction, category) =>
                {
                    transaction.Category = category;
                    return transaction;
                },
                splitOn: "Id");

            return transactions;
        }

        public virtual async Task<T?> GetByIdAsync(int id)
        {
            using var connection = _context.CreateConnection();
            var sql = $@"
                SELECT t.*, c.* 
                FROM {_tableName} t
                LEFT JOIN Categories c ON t.CategoryId = c.Id
                WHERE t.Id = @Id";

            var transactions = await connection.QueryAsync<T, Category, T>(
                sql,
                (transaction, category) =>
                {
                    transaction.Category = category;
                    return transaction;
                },
                new { Id = id },
                splitOn: "Id");

            return transactions.FirstOrDefault();
        }

        public abstract Task<int> AddAsync(T entity);
        public abstract Task<bool> UpdateAsync(T entity);
        
        public virtual async Task<bool> DeleteAsync(int id)
        {
            using var connection = _context.CreateConnection();
            var sql = $"DELETE FROM {_tableName} WHERE Id = @Id";
            var affected = await connection.ExecuteAsync(sql, new { Id = id });
            return affected > 0;
        }

        public virtual async Task<IEnumerable<T>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
        {
            using var connection = _context.CreateConnection();
            var sql = $@"
                SELECT t.*, c.* 
                FROM {_tableName} t
                LEFT JOIN Categories c ON t.CategoryId = c.Id
                WHERE t.Date BETWEEN @StartDate AND @EndDate
                ORDER BY t.Date DESC";

            var transactions = await connection.QueryAsync<T, Category, T>(
                sql,
                (transaction, category) =>
                {
                    transaction.Category = category;
                    return transaction;
                },
                new { StartDate = startDate.ToString("yyyy-MM-dd"), EndDate = endDate.ToString("yyyy-MM-dd") },
                splitOn: "Id");

            return transactions;
        }
    }
}