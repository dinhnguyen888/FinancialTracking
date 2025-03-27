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
    public class IncomeViewModel : ViewModelBase
    {
        private readonly IIncomeRepository _incomeRepository;
        private readonly ICategoryRepository _categoryRepository;
        private ObservableCollection<Income> _incomes;
        private ObservableCollection<Category> _categories;
        private Income? _selectedIncome;
        private decimal _totalIncome;

        public IncomeViewModel(IIncomeRepository incomeRepository, ICategoryRepository categoryRepository)
        {
            _incomeRepository = incomeRepository;
            _categoryRepository = categoryRepository;
            _incomes = new ObservableCollection<Income>();
            _categories = new ObservableCollection<Category>();

            AddIncomeCommand = new RelayCommand(_ => AddIncome());
            EditIncomeCommand = new RelayCommand(_ => EditIncome(), _ => SelectedIncome != null);
            DeleteIncomeCommand = new RelayCommand(_ => DeleteIncome(), _ => SelectedIncome != null);
            ReloadDataCommand = new RelayCommand(_ => LoadDataAsync());

            LoadDataAsync();
        }

        public ObservableCollection<Income> Incomes
        {
            get => _incomes;
            set => SetProperty(ref _incomes, value);
        }

        public ObservableCollection<Category> Categories
        {
            get => _categories;
            set => SetProperty(ref _categories, value);
        }

        public Income? SelectedIncome
        {
            get => _selectedIncome;
            set
            {
                if (SetProperty(ref _selectedIncome, value))
                {
                    ((RelayCommand)EditIncomeCommand).RaiseCanExecuteChanged();
                    ((RelayCommand)DeleteIncomeCommand).RaiseCanExecuteChanged();
                }
            }
        }

        public decimal TotalIncome
        {
            get => _totalIncome;
            set => SetProperty(ref _totalIncome, value);
        }

        public ICommand AddIncomeCommand { get; }
        public ICommand EditIncomeCommand { get; }
        public ICommand DeleteIncomeCommand { get; }
        public ICommand ReloadDataCommand { get; }

        public async void LoadDataAsync()
        {
            try
            {
                var incomes = await _incomeRepository.GetAllAsync();
                var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Income);
                
                Incomes = new ObservableCollection<Income>(incomes);
                Categories = new ObservableCollection<Category>(categories);

                var now = DateTime.Now;
                TotalIncome = await _incomeRepository.GetTotalForMonthAsync(now.Year, now.Month);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi tải dữ liệu: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void AddIncome()
        {
            var viewModel = new TransactionDialogViewModel(true);
            var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Income);
            viewModel.SetCategories(categories);

            var dialog = new TransactionDialog(viewModel);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true && viewModel.Result is Income income)
            {
                try
                {
                    income.Id = await _incomeRepository.AddAsync(income);
                    Incomes.Add(income);
                    await UpdateTotalAsync();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi thêm thu nhập: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void EditIncome()
        {
            if (SelectedIncome == null) return;

            var viewModel = new TransactionDialogViewModel(true, SelectedIncome);
            var categories = await _categoryRepository.GetByCategoryTypeAsync(CategoryType.Income);
            viewModel.SetCategories(categories);

            var dialog = new TransactionDialog(viewModel);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true && viewModel.Result is Income income)
            {
                try
                {
                    income.Id = SelectedIncome.Id;
                    if (await _incomeRepository.UpdateAsync(income))
                    {
                        var index = Incomes.IndexOf(SelectedIncome);
                        Incomes[index] = income;
                        await UpdateTotalAsync();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi cập nhật thu nhập: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void DeleteIncome()
        {
            if (SelectedIncome == null) return;

            var result = MessageBox.Show(
                "Bạn có chắc chắn muốn xóa khoản thu nhập này không?",
                "Xác nhận xóa",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    if (await _incomeRepository.DeleteAsync(SelectedIncome.Id))
                    {
                        Incomes.Remove(SelectedIncome);
                        await UpdateTotalAsync();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi xóa thu nhập: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async Task UpdateTotalAsync()
        {
            var now = DateTime.Now;
            TotalIncome = await _incomeRepository.GetTotalForMonthAsync(now.Year, now.Month);
        }
    }
}