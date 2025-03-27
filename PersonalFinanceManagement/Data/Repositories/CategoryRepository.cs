using Dapper;
using PersonalFinanceManagement.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace PersonalFinanceManagement.Data.Repositories
{
    public interface ICategoryRepository : IRepository<Category>
    {
        Task<IEnumerable<Category>> GetByCategoryTypeAsync(CategoryType type);
    }

    public class CategoryRepository : ICategoryRepository
    {
        private readonly IDatabaseContext _context;

        public CategoryRepository(IDatabaseContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Category>> GetAllAsync()
        {
            using var connection = _context.CreateConnection();
            return await connection.QueryAsync<Category>("SELECT * FROM Categories WHERE IsActive = 1");
        }

        public async Task<Category?> GetByIdAsync(int id)
        {
            using var connection = _context.CreateConnection();
            return await connection.QuerySingleOrDefaultAsync<Category>(
                "SELECT * FROM Categories WHERE Id = @Id", new { Id = id });
        }

        public async Task<IEnumerable<Category>> GetByCategoryTypeAsync(CategoryType type)
        {
            using var connection = _context.CreateConnection();
            return await connection.QueryAsync<Category>(
                "SELECT * FROM Categories WHERE Type = @Type AND IsActive = 1", 
                new { Type = (int)type });
        }

        public async Task<int> AddAsync(Category category)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                INSERT INTO Categories (Name, Description, Type, IsActive) 
                VALUES (@Name, @Description, @Type, @IsActive);
                SELECT last_insert_rowid();";
            
            return await connection.QuerySingleAsync<int>(sql, category);
        }

        public async Task<bool> UpdateAsync(Category category)
        {
            using var connection = _context.CreateConnection();
            var sql = @"
                UPDATE Categories 
                SET Name = @Name, 
                    Description = @Description, 
                    Type = @Type, 
                    IsActive = @IsActive 
                WHERE Id = @Id";

            var affected = await connection.ExecuteAsync(sql, category);
            return affected > 0;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            using var connection = _context.CreateConnection();
            // Soft delete - just mark as inactive
            var sql = "UPDATE Categories SET IsActive = 0 WHERE Id = @Id";
            var affected = await connection.ExecuteAsync(sql, new { Id = id });
            return affected > 0;
        }
    }
}