using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows;
using System.Windows.Input;
using PersonalFinanceManagement.Data.Repositories;
using PersonalFinanceManagement.Models;
using PersonalFinanceManagement.Views.Dialogs;

namespace PersonalFinanceManagement.ViewModels.Dialogs
{
    public class CategoryManagementViewModel : ViewModelBase
    {
        private readonly ICategoryRepository _categoryRepository;
        private ObservableCollection<Category> _categories;
        private Category? _selectedCategory;
        private CategoryType _selectedTypeFilter;

        public CategoryManagementViewModel(ICategoryRepository categoryRepository)
        {
            _categoryRepository = categoryRepository;
            _categories = new ObservableCollection<Category>();
            _selectedTypeFilter = CategoryType.Expense;

            AddCategoryCommand = new RelayCommand(_ => AddCategory());
            EditCategoryCommand = new RelayCommand(_ => EditCategory(), _ => SelectedCategory != null);
            DeleteCategoryCommand = new RelayCommand(_ => DeleteCategory(), _ => SelectedCategory != null);
            CloseCommand = new RelayCommand(_ => Close());

            LoadCategories();
        }

        public ObservableCollection<Category> Categories
        {
            get => _categories;
            set => SetProperty(ref _categories, value);
        }

        public Category? SelectedCategory
        {
            get => _selectedCategory;
            set
            {
                if (SetProperty(ref _selectedCategory, value))
                {
                    ((RelayCommand)EditCategoryCommand).RaiseCanExecuteChanged();
                    ((RelayCommand)DeleteCategoryCommand).RaiseCanExecuteChanged();
                }
            }
        }

        public CategoryType SelectedTypeFilter
        {
            get => _selectedTypeFilter;
            set
            {
                if (SetProperty(ref _selectedTypeFilter, value))
                {
                    LoadCategories();
                }
            }
        }

        public Array CategoryTypes => Enum.GetValues(typeof(CategoryType));

        public ICommand AddCategoryCommand { get; }
        public ICommand EditCategoryCommand { get; }
        public ICommand DeleteCategoryCommand { get; }
        public ICommand CloseCommand { get; }

        public event EventHandler? DialogClosed;

        private async void LoadCategories()
        {
            try
            {
                var categories = await _categoryRepository.GetByCategoryTypeAsync(SelectedTypeFilter);
                Categories = new ObservableCollection<Category>(categories.OrderBy(c => c.Name));
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi tải danh mục: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void AddCategory()
        {
            var viewModel = new CategoryDialogViewModel { SelectedType = SelectedTypeFilter };
            var dialog = new CategoryDialog(viewModel);

            if (Application.Current.MainWindow != null)
            {
                dialog.Owner = Application.Current.MainWindow;
            }

            if (dialog.ShowDialog() == true && viewModel.Result != null)
            {
                try
                {
                    var category = viewModel.Result;
                    category.Id = await _categoryRepository.AddAsync(category);
                    LoadCategories();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi thêm danh mục: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void EditCategory()
        {
            if (SelectedCategory == null) return;

            var viewModel = new CategoryDialogViewModel(SelectedCategory);
            var dialog = new CategoryDialog(viewModel);

            if (Application.Current.MainWindow != null)
            {
                dialog.Owner = Application.Current.MainWindow;
            }

            if (dialog.ShowDialog() == true && viewModel.Result != null)
            {
                try
                {
                    var category = viewModel.Result;
                    category.Id = SelectedCategory.Id;
                    
                    if (await _categoryRepository.UpdateAsync(category))
                    {
                        LoadCategories();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi cập nhật danh mục: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void DeleteCategory()
        {
            if (SelectedCategory == null) return;

            var result = MessageBox.Show(
                "Bạn có chắc chắn muốn xóa danh mục này không?",
                "Xác nhận xóa",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    if (await _categoryRepository.DeleteAsync(SelectedCategory.Id))
                    {
                        LoadCategories();
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Lỗi xóa danh mục: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void Close()
        {
            DialogClosed?.Invoke(this, EventArgs.Empty);
        }
    }
}