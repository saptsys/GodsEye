using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Threading;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using System.Linq;
using Data_Viewer.ViewModels;
using System.ComponentModel;

namespace Data_Viewer
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private MainWindowVM ViewModel;
        public MainWindow()
        {
            InitializeComponent();
            DataContext = ViewModel = new MainWindowVM();
            mainGrid.Focus();
        }

        private void mainGrid_SelectionChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e)
        {
            ViewModel.Records_SelectionChanged(sender, e);
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            base.OnClosing(e);
            ViewModel.OnClosing(e);
        }

        private void Window_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if(e.Key == Key.Escape)
                this.Close();
        }

    }
}
