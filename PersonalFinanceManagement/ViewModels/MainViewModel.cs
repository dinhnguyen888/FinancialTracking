using System;
using System.Windows.Input;
using PersonalFinanceManagement.Data.Repositories;
using PersonalFinanceManagement.Services;
using PersonalFinanceManagement.Views.Dialogs;
using PersonalFinanceManagement.ViewModels.Dialogs;

namespace PersonalFinanceManagement.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private readonly ICategoryRepository _categoryRepository;
        private readonly IIncomeRepository _incomeRepository;
        private readonly IExpenseRepository _expenseRepository;
        private readonly IExportService _exportService;
        private readonly IThemeService _themeService;
        private ViewModelBase? _currentViewModel;
        private decimal _currentBalance;

        public MainViewModel(
            ICategoryRepository categoryRepository,
            IIncomeRepository incomeRepository,
            IExpenseRepository expenseRepository,
            IExportService exportService,
            IThemeService themeService)
        {
            _categoryRepository = categoryRepository;
            _incomeRepository = incomeRepository;
            _expenseRepository = expenseRepository;
            _exportService = exportService;
            _themeService = themeService;

            // Initialize commands
            NavigateIncomeCommand = new RelayCommand(_ => NavigateTo("Income"));
            NavigateExpenseCommand = new RelayCommand(_ => NavigateTo("Expense"));
            NavigateReportCommand = new RelayCommand(_ => NavigateTo("Report"));
            ManageCategoriesCommand = new RelayCommand(_ => ShowCategoryManagementDialog());

            // Load initial view and balance
            NavigateTo("Income");
            UpdateBalanceAsync();
        }

        public ViewModelBase? CurrentViewModel
        {
            get => _currentViewModel;
            set => SetProperty(ref _currentViewModel, value);
        }

        public decimal CurrentBalance
        {
            get => _currentBalance;
            set => SetProperty(ref _currentBalance, value);
        }



        public ICommand NavigateIncomeCommand { get; }
        public ICommand NavigateExpenseCommand { get; }
        public ICommand NavigateReportCommand { get; }
        public ICommand ManageCategoriesCommand { get; }
        public ICommand ToggleThemeCommand { get; }

        private async void UpdateBalanceAsync()
        {
            try
            {
                var now = DateTime.Now;
                var totalIncome = await _incomeRepository.GetTotalForMonthAsync(now.Year, now.Month);
                var totalExpense = await _expenseRepository.GetTotalForMonthAsync(now.Year, now.Month);
                CurrentBalance = totalIncome - totalExpense;
            }
            catch (Exception)
            {
                CurrentBalance = 0;
            }
        }

        private void NavigateTo(string viewName)
        {
            ViewModelBase? newViewModel = viewName switch
            {
                "Income" => new IncomeViewModel(_incomeRepository, _categoryRepository),
                "Expense" => new ExpenseViewModel(_expenseRepository, _categoryRepository),
                "Report" => new ReportViewModel(_incomeRepository, _expenseRepository, _categoryRepository, _exportService, _themeService),
                _ => CurrentViewModel
            };

            if (newViewModel != null)
            {
                // Subscribe to transaction changes to update balance
                if (newViewModel is IncomeViewModel incomeViewModel)
                {
                    incomeViewModel.PropertyChanged += (s, e) =>
                    {
                        if (e.PropertyName == nameof(IncomeViewModel.TotalIncome))
                        {
                            UpdateBalanceAsync();
                        }
                    };
                }
                else if (newViewModel is ExpenseViewModel expenseViewModel)
                {
                    expenseViewModel.PropertyChanged += (s, e) =>
                    {
                        if (e.PropertyName == nameof(ExpenseViewModel.TotalExpense))
                        {
                            UpdateBalanceAsync();
                        }
                    };
                }

                CurrentViewModel = newViewModel;
            }
        }

        private void ShowCategoryManagementDialog()
        {
            var viewModel = new CategoryManagementViewModel(_categoryRepository);
            var dialog = new CategoryManagementDialog(viewModel);
            dialog.Owner = System.Windows.Application.Current.MainWindow;
            dialog.ShowDialog();

            // Refresh current view if it's affected by category changes
            if (CurrentViewModel != null)
            {
                if (CurrentViewModel is IncomeViewModel incomeVm)
                {
                    incomeVm.ReloadDataCommand.Execute(null);
                }
                else if (CurrentViewModel is ExpenseViewModel expenseVm)
                {
                    expenseVm.ReloadDataCommand.Execute(null);
                }
                else if (CurrentViewModel is ReportViewModel reportVm)
                {
                    reportVm.RefreshCommand.Execute(null);
                }
            }
        }
    }
}