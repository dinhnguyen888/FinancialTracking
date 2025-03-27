using System.Windows;

namespace PersonalFinanceManagement.Services
{
    public interface IThemeService
    {
        void InitializeTheme();
    }

    public class ThemeService : IThemeService
    {
        public void InitializeTheme()
        {
            var app = Application.Current;
            app.Resources.MergedDictionaries[0].Source =
                new Uri("/Themes/LightTheme.xaml", UriKind.Relative);
        }
    }
}