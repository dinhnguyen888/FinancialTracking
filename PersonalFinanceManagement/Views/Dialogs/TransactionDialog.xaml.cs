using System.Windows;
using PersonalFinanceManagement.ViewModels.Dialogs;

namespace PersonalFinanceManagement.Views.Dialogs
{
    public partial class TransactionDialog : Window
    {
        public TransactionDialog(TransactionDialogViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
            viewModel.DialogClosed += (s, e) => DialogResult = viewModel.Result != null;
        }
    }
}