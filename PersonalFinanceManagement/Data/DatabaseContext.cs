using System.Data;
using System.Data.SQLite;
using System.IO;
using Dapper;
using PersonalFinanceManagement.Models;

namespace PersonalFinanceManagement.Data
{
    public interface IDatabaseContext
    {
        IDbConnection CreateConnection();
    }

    public class DatabaseContext : IDatabaseContext
    {
        private readonly string _connectionString;
        private readonly string _databasePath;

        public DatabaseContext()
        {
            // Create database in AppData folder
            var appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "PersonalFinanceManagement");

            // Create directory if it doesn't exist
            if (!Directory.Exists(appDataPath))
            {
                Directory.CreateDirectory(appDataPath);
            }

            _databasePath = Path.Combine(appDataPath, "FinanceDB.sqlite");
            _connectionString = $"Data Source={_databasePath};Version=3;";

            InitializeDatabase();
        }

        public IDbConnection CreateConnection()
        {
            return new SQLiteConnection(_connectionString);
        }

        private void InitializeDatabase()
        {
            var isNewDatabase = !File.Exists(_databasePath);

            if (isNewDatabase)
            {
                SQLiteConnection.CreateFile(_databasePath);
            }

            using var connection = CreateConnection();
            connection.Open();

            if (isNewDatabase)
            {
                // Create Categories table
                connection.Execute(@"
                    CREATE TABLE IF NOT EXISTS Categories (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT NOT NULL,
                        Description TEXT,
                        Type INTEGER NOT NULL,
                        IsActive INTEGER NOT NULL DEFAULT 1
                    )");

                // Create Incomes table
                connection.Execute(@"
                    CREATE TABLE IF NOT EXISTS Incomes (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Amount DECIMAL NOT NULL,
                        Date TEXT NOT NULL,
                        Description TEXT,
                        CategoryId INTEGER,
                        Source TEXT,
                        FOREIGN KEY(CategoryId) REFERENCES Categories(Id)
                    )");

                // Create Expenses table
                connection.Execute(@"
                    CREATE TABLE IF NOT EXISTS Expenses (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Amount DECIMAL NOT NULL,
                        Date TEXT NOT NULL,
                        Description TEXT,
                        CategoryId INTEGER,
                        IsEssential INTEGER NOT NULL DEFAULT 0,
                        PaymentMethod TEXT,
                        FOREIGN KEY(CategoryId) REFERENCES Categories(Id)
                    )");

                // Insert default categories
                InsertDefaultCategories(connection);
            }
        }

        private void InsertDefaultCategories(IDbConnection connection)
        {
            // Income Categories
            var incomeCategories = new[]
            {
                new { Name = "Salary", Description = "Regular employment income", Type = CategoryType.Income },
                new { Name = "Bonus", Description = "Additional work compensation", Type = CategoryType.Income },
                new { Name = "Investment", Description = "Returns from investments", Type = CategoryType.Income },
                new { Name = "Freelance", Description = "Income from freelance work", Type = CategoryType.Income },
                new { Name = "Other Income", Description = "Miscellaneous income", Type = CategoryType.Income }
            };

            // Expense Categories
            var expenseCategories = new[]
            {
                new { Name = "Food & Dining", Description = "Meals and groceries", Type = CategoryType.Expense },
                new { Name = "Transportation", Description = "Public transport and fuel", Type = CategoryType.Expense },
                new { Name = "Housing", Description = "Rent and utilities", Type = CategoryType.Expense },
                new { Name = "Entertainment", Description = "Movies, games, and hobbies", Type = CategoryType.Expense },
                new { Name = "Healthcare", Description = "Medical expenses", Type = CategoryType.Expense },
                new { Name = "Shopping", Description = "Clothing and personal items", Type = CategoryType.Expense },
                new { Name = "Education", Description = "Books and courses", Type = CategoryType.Expense },
                new { Name = "Bills", Description = "Regular monthly bills", Type = CategoryType.Expense },
                new { Name = "Other Expenses", Description = "Miscellaneous expenses", Type = CategoryType.Expense }
            };

            var insertSql = @"
                INSERT INTO Categories (Name, Description, Type, IsActive) 
                VALUES (@Name, @Description, @Type, 1)";

            foreach (var category in incomeCategories.Concat(expenseCategories))
            {
                connection.Execute(insertSql, new
                {
                    category.Name,
                    category.Description,
                    Type = (int)category.Type
                });
            }
        }
    }
}