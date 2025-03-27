using Microsoft.Extensions.DependencyInjection;
using PersonalFinanceManagement.Data;
using PersonalFinanceManagement.Data.Repositories;
using PersonalFinanceManagement.ViewModels;
using PersonalFinanceManagement.Services;
using System.Windows;

namespace PersonalFinanceManagement
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            ConfigureServices();
        }

        private void ConfigureServices()
        {
            var services = new ServiceCollection();

            // Register database context
            services.AddSingleton<IDatabaseContext, DatabaseContext>();

            // Register repositories
            services.AddScoped<ICategoryRepository, CategoryRepository>();
            services.AddScoped<IIncomeRepository, IncomeRepository>();
            services.AddScoped<IExpenseRepository, ExpenseRepository>();

            // Register services
            services.AddSingleton<IThemeService, ThemeService>();
            services.AddScoped<IExportService, ExportService>();

            // Register ViewModels
            services.AddScoped<MainViewModel>();
            services.AddScoped<IncomeViewModel>();
            services.AddScoped<ExpenseViewModel>();
            services.AddScoped<ReportViewModel>();

            var serviceProvider = services.BuildServiceProvider();

            // Set DataContext to MainViewModel
            DataContext = serviceProvider.GetRequiredService<MainViewModel>();
        }


    }
}