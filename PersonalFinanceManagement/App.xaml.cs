using System;
using System.Windows;

namespace PersonalFinanceManagement
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Set up global exception handling
            AppDomain.CurrentDomain.UnhandledException += (s, args) =>
            {
                MessageBox.Show($"An unexpected error occurred: {args.ExceptionObject}",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
            };

            Current.DispatcherUnhandledException += (s, args) =>
            {
                MessageBox.Show($"An unexpected error occurred: {args.Exception.Message}",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
                args.Handled = true;
            };
        }
    }
}
