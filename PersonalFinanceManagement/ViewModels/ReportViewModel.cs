using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;
using System.Windows;
using OxyPlot;
using OxyPlot.Axes;
using OxyPlot.Series;
using PersonalFinanceManagement.Data.Repositories;
using PersonalFinanceManagement.Models;
using PersonalFinanceManagement.Services;

namespace PersonalFinanceManagement.ViewModels
{
    public class ReportViewModel : ViewModelBase
    {
        private readonly IIncomeRepository _incomeRepository;
        private readonly IExpenseRepository _expenseRepository;
        private readonly ICategoryRepository _categoryRepository;
        private readonly IExportService _exportService;
        private DateTime _startDate;
        private DateTime _endDate;
        private PlotModel _expensesByCategoryChart;
        private PlotModel _monthlyComparisonChart;
        private decimal _totalIncome;
        private decimal _totalExpenses;
        private decimal _balance;
        private bool _isExporting;

        public ReportViewModel(
            IIncomeRepository incomeRepository,
            IExpenseRepository expenseRepository,
            ICategoryRepository categoryRepository,
            IExportService exportService,
            IThemeService themeService)
        {
            _incomeRepository = incomeRepository;
            _expenseRepository = expenseRepository;
            _categoryRepository = categoryRepository;
            _exportService = exportService;

            // Initialize dates to current month
            _startDate = new DateTime(DateTime.Now.Year, DateTime.Now.Month, 1);
            _endDate = _startDate.AddMonths(1).AddDays(-1);

            _expensesByCategoryChart = new PlotModel { Title = "Expenses by Category" };
            _monthlyComparisonChart = new PlotModel { Title = "Monthly Income vs Expenses" };

            RefreshCommand = new RelayCommand(_ => LoadChartsAsync());
            ExportCommand = new RelayCommand(_ => ExportReportAsync(), _ => !_isExporting);

            LoadChartsAsync();
        }

        public DateTime StartDate
        {
            get => _startDate;
            set
            {
                if (SetProperty(ref _startDate, value))
                {
                    LoadChartsAsync();
                }
            }
        }

        public DateTime EndDate
        {
            get => _endDate;
            set
            {
                if (SetProperty(ref _endDate, value))
                {
                    LoadChartsAsync();
                }
            }
        }

        public PlotModel ExpensesByCategoryChart
        {
            get => _expensesByCategoryChart;
            set => SetProperty(ref _expensesByCategoryChart, value);
        }

        public PlotModel MonthlyComparisonChart
        {
            get => _monthlyComparisonChart;
            set => SetProperty(ref _monthlyComparisonChart, value);
        }

        public decimal TotalIncome
        {
            get => _totalIncome;
            set => SetProperty(ref _totalIncome, value);
        }

        public decimal TotalExpenses
        {
            get => _totalExpenses;
            set => SetProperty(ref _totalExpenses, value);
        }

        public decimal Balance
        {
            get => _balance;
            set => SetProperty(ref _balance, value);
        }

        public ICommand RefreshCommand { get; }
        public ICommand ExportCommand { get; }

        private async void LoadChartsAsync()
        {
            try
            {
                await LoadExpensesByCategoryChartAsync();
                await LoadMonthlyComparisonChartAsync();
                await UpdateTotalsAsync();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading charts: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async Task LoadExpensesByCategoryChartAsync()
        {
            var expenseCategories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Expense);
            var plotModel = new PlotModel 
            { 
                Title = "Expenses by Category",
                TitleFontSize = 16
            };

            var series = new PieSeries
            {
                StrokeThickness = 2.0,
                InsideLabelPosition = 0.8,
                AngleSpan = 360,
                StartAngle = 0,
                FontSize = 12
            };

            foreach (var category in expenseCategories)
            {
                var total = await _expenseRepository.GetTotalByCategory(category.Id);
                if (total > 0)
                {
                    series.Slices.Add(new PieSlice(category.Name, (double)total)
                    {
                        IsExploded = true
                    });
                }
            }

            plotModel.Series.Add(series);
            ExpensesByCategoryChart = plotModel;
        }

        private async Task LoadMonthlyComparisonChartAsync()
        {
            var plotModel = new PlotModel
            {
                Title = "Monthly Income vs Expenses",
                TitleFontSize = 16
            };

            var categoryAxis = new CategoryAxis
            {
                Position = AxisPosition.Left,
                Title = "Month",
                TitleFontSize = 12,
                FontSize = 12
            };

            var valueAxis = new LinearAxis
            {
                Position = AxisPosition.Bottom,
                Title = "Amount",
                TitleFontSize = 12,
                FontSize = 12,
                StringFormat = "C0"
            };

            plotModel.Axes.Add(categoryAxis);
            plotModel.Axes.Add(valueAxis);

            var startDate = StartDate.Date;
            var endDate = EndDate.Date;
            var months = new List<DateTime>();
            var currentDate = startDate;

            while (currentDate <= endDate)
            {
                months.Add(currentDate);
                currentDate = currentDate.AddMonths(1);
            }

            var incomeSeries = new BarSeries
            {
                Title = "Income",
                FillColor = OxyColor.FromRgb(46, 204, 113),
                StrokeColor = OxyColor.FromRgb(39, 174, 96),
                StrokeThickness = 1
            };

            var expenseSeries = new BarSeries
            {
                Title = "Expenses",
                FillColor = OxyColor.FromRgb(231, 76, 60),
                StrokeColor = OxyColor.FromRgb(192, 57, 43),
                StrokeThickness = 1
            };

            foreach (var month in months)
            {
                var income = await _incomeRepository.GetTotalForMonthAsync(month.Year, month.Month);
                var expense = await _expenseRepository.GetTotalForMonthAsync(month.Year, month.Month);
                
                categoryAxis.Labels.Add(month.ToString("MMM yyyy"));
                incomeSeries.Items.Add(new BarItem((double)income));
                expenseSeries.Items.Add(new BarItem((double)expense));
            }

            plotModel.Series.Add(incomeSeries);
            plotModel.Series.Add(expenseSeries);

            MonthlyComparisonChart = plotModel;
        }

        private async Task UpdateTotalsAsync()
        {
            var now = DateTime.Now;
            TotalIncome = await _incomeRepository.GetTotalForMonthAsync(now.Year, now.Month);
            TotalExpenses = await _expenseRepository.GetTotalForMonthAsync(now.Year, now.Month);
            Balance = TotalIncome - TotalExpenses;
        }

        private async void ExportReportAsync()
        {
            try
            {
                _isExporting = true;
                ((RelayCommand)ExportCommand).RaiseCanExecuteChanged();

                var incomes = await _incomeRepository.GetAllAsync();
                var expenses = await _expenseRepository.GetAllAsync();

                await _exportService.ExportToExcelAsync(incomes, expenses, StartDate, EndDate);
                MessageBox.Show("Report exported successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting report: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                _isExporting = false;
                ((RelayCommand)ExportCommand).RaiseCanExecuteChanged();
            }
        }
    }
}