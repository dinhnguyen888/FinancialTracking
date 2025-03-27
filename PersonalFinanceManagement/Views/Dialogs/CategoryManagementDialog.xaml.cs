using System.Windows;
using PersonalFinanceManagement.ViewModels.Dialogs;

namespace PersonalFinanceManagement.Views.Dialogs
{
    public partial class CategoryManagementDialog : Window
    {
        public CategoryManagementDialog(CategoryManagementViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
            viewModel.DialogClosed += (s, e) => Close();
        }
    }
}