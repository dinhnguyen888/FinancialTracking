using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Input;
using PersonalFinanceManagement.Models;

namespace PersonalFinanceManagement.ViewModels.Dialogs
{
    public class CategoryDialogViewModel : ViewModelBase, IDataErrorInfo
    {
        private string _dialogTitle;
        private string _name;
        private string _description;
        private CategoryType _selectedType;
        private bool _isSaving;

        public CategoryDialogViewModel(Category? category = null)
        {
            _dialogTitle = category == null ? "Thêm Danh Mục" : "Sửa Danh Mục";
            
            if (category != null)
            {
                _name = category.Name;
                _description = category.Description;
                _selectedType = category.Type;
            }
            else
            {
                _name = string.Empty;
                _description = string.Empty;
                _selectedType = CategoryType.Expense;
            }

            SaveCommand = new RelayCommand(_ => Save(), _ => CanSave());
            CancelCommand = new RelayCommand(_ => Cancel());
        }

        public string DialogTitle
        {
            get => _dialogTitle;
            set => SetProperty(ref _dialogTitle, value);
        }

        public string Name
        {
            get => _name;
            set => SetProperty(ref _name, value);
        }

        public string Description
        {
            get => _description;
            set => SetProperty(ref _description, value);
        }

        public CategoryType SelectedType
        {
            get => _selectedType;
            set => SetProperty(ref _selectedType, value);
        }

        public Array CategoryTypes => Enum.GetValues(typeof(CategoryType));

        public ICommand SaveCommand { get; }
        public ICommand CancelCommand { get; }

        public event EventHandler? DialogClosed;
        public Category? Result { get; private set; }

        #region IDataErrorInfo Implementation

        public string Error => string.Empty;

        public string this[string columnName]
        {
            get
            {
                return columnName switch
                {
                    nameof(Name) => ValidateName(),
                    _ => string.Empty
                };
            }
        }

        private string ValidateName()
        {
            if (string.IsNullOrWhiteSpace(Name))
            {
                return "Vui lòng nhập tên danh mục";
            }
            return string.Empty;
        }

        #endregion

        private bool CanSave()
        {
            if (_isSaving) return false;
            if (string.IsNullOrWhiteSpace(Name)) return false;
            return true;
        }

        private void Save()
        {
            if (_isSaving) return;
            _isSaving = true;

            try
            {
                Result = new Category
                {
                    Name = Name.Trim(),
                    Description = Description?.Trim() ?? string.Empty,
                    Type = SelectedType,
                    IsActive = true
                };

                DialogClosed?.Invoke(this, EventArgs.Empty);
            }
            finally
            {
                _isSaving = false;
            }
        }

        private void Cancel()
        {
            Result = null;
            DialogClosed?.Invoke(this, EventArgs.Empty);
        }
    }
}