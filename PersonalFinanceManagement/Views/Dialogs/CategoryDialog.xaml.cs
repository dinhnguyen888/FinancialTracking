using System.Windows;
using PersonalFinanceManagement.ViewModels.Dialogs;

namespace PersonalFinanceManagement.Views.Dialogs
{
    public partial class CategoryDialog : Window
    {
        public CategoryDialog(CategoryDialogViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
            viewModel.DialogClosed += (s, e) => DialogResult = viewModel.Result != null;
        }
    }
}