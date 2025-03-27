using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Windows;
using PersonalFinanceManagement.Data.Repositories;
using PersonalFinanceManagement.Models;
using PersonalFinanceManagement.Views.Dialogs;
using PersonalFinanceManagement.ViewModels.Dialogs;

namespace PersonalFinanceManagement.ViewModels
{
    public class ExpenseViewModel : ViewModelBase
    {
        private readonly IExpenseRepository _expenseRepository;
        private readonly ICategoryRepository _categoryRepository;
        private ObservableCollection<Expense> _expenses;
        private ObservableCollection<Category> _categories;
        private Expense? _selectedExpense;
        private decimal _totalExpense;

        public ExpenseViewModel(IExpenseRepository expenseRepository, ICategoryRepository categoryRepository)
        {
            _expenseRepository = expenseRepository;
            _categoryRepository = categoryRepository;
            _expenses = new ObservableCollection<Expense>();
            _categories = new ObservableCollection<Category>();

            AddExpenseCommand = new RelayCommand(_ => AddExpense());
            EditExpenseCommand = new RelayCommand(_ => EditExpense(), _ => SelectedExpense != null);
            DeleteExpenseCommand = new RelayCommand(_ => DeleteExpense(), _ => SelectedExpense != null);
            ReloadDataCommand = new RelayCommand(_ => LoadDataAsync());

            LoadDataAsync();
        }

        public ObservableCollection<Expense> Expenses
        {
            get => _expenses;
            set => SetProperty(ref _expenses, value);
        }

        public ObservableCollection<Category> Categories
        {
            get => _categories;
            set => SetProperty(ref _categories, value);
        }

        public Expense? SelectedExpense
        {
            get => _selectedExpense;
            set
            {
                if (SetProperty(ref _selectedExpense, value))
                {
                    ((RelayCommand)EditExpenseCommand).RaiseCanExecuteChanged();
                    ((RelayCommand)DeleteExpenseCommand).RaiseCanExecuteChanged();
                }
            }
        }

        public decimal TotalExpense
        {
            get => _totalExpense;
            set => SetProperty(ref _totalExpense, value);
        }

        public ICommand AddExpenseCommand { get; }
        public ICommand EditExpenseCommand { get; }
        public ICommand DeleteExpenseCommand { get; }
        public ICommand ReloadDataCommand { get; }

        public async void LoadDataAsync()
        {
            try
            {
                var expenses = await _expenseRepository.GetAllAsync();
                var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Expense);
                
                Expenses = new ObservableCollection<Expense>(expenses);
                Categories = new ObservableCollection<Category>(categories);

                var now = DateTime.Now;
                TotalExpense = await _expenseRepository.GetTotalForMonthAsync(now.Year, now.Month);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi tải dữ liệu: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void AddExpense()
        {
            var viewModel = new TransactionDialogViewModel(false);
            var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Expense);
            viewModel.SetCategories(categories);

            var dialog = new TransactionDialog(viewModel);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true && viewModel.Result is Expense expense)
            {
                try
                {
                    expense.Id = await _expenseRepository.AddAsync(expense);
                    Expenses.Add(expense);
                    await UpdateTotalAsync();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi thêm chi tiêu: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void EditExpense()
        {
            if (SelectedExpense == null) return;

            var viewModel = new TransactionDialogViewModel(false, SelectedExpense);
            var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Expense);
            viewModel.SetCategories(categories);

            var dialog = new TransactionDialog(viewModel);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true && viewModel.Result is Expense expense)
            {
                try
                {
                    expense.Id = SelectedExpense.Id;
                    if (await _expenseRepository.UpdateAsync(expense))
                    {
                        var index = Expenses.IndexOf(SelectedExpense);
                        Expenses[index] = expense;
                        await UpdateTotalAsync();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi cập nhật chi tiêu: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void DeleteExpense()
        {
            if (SelectedExpense == null) return;

            var result = MessageBox.Show(
                "Bạn có chắc chắn muốn xóa khoản chi tiêu này không?",
                "Xác nhận xóa",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    if (await _expenseRepository.DeleteAsync(SelectedExpense.Id))
                    {
                        Expenses.Remove(SelectedExpense);
                        await UpdateTotalAsync();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi xóa chi tiêu: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async Task UpdateTotalAsync()
        {
            var now = DateTime.Now;
            TotalExpense = await _expenseRepository.GetTotalForMonthAsync(now.Year, now.Month);
        }
    }
}