using Data_Viewer.Common;
using Data_Viewer.Entities;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data.SQLite;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace Data_Viewer.ViewModels
{
    public class MainWindowVM : BaseViewModel
    {
        private string SoftwarePath;
        private string SQLitePath;

        private Dictionary<string, string> Settings;

        private DispatcherTimer timer;

        private SQLiteConnection Con;

        public MainWindowVM()
        {
            var di = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            SoftwarePath = di.Parent.Parent.Parent.Parent.FullName;
            Settings = LoadJson(SoftwarePath + "\\settings.json");

            //Data Source = c:\mydb.db; Version = 3; Read Only = True;
            SQLitePath = "Data Source=" + (SoftwarePath + "\\" + Settings["dataBase"]).Replace("\\", "/")+ "; Version = 3; Read Only = True;";
            Con = new SQLiteConnection(SQLitePath);
            FillData();

            timer = new DispatcherTimer();
            timer.Interval = new TimeSpan(0, 0, 1);
            timer.Tick += Timer_Tick;
            timer.Start();
        }

        public void OnClosing(CancelEventArgs e)
        {
            if (Con.State == System.Data.ConnectionState.Open)
                Con.Close();
        }

        public void Records_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.AddedItems.Count == 0)
                return;
            e.Handled = true;
            if (e.AddedItems[0] is Plate item)
            {
                ShowDetails(item.Id);
            }
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            timer.Stop();

            FillData();

            timer.Start();
        }


        private ObservableCollection<Plate> _Records;
        public ObservableCollection<Plate> Records
        {
            get
            {
                if (_Records == null)
                {
                    _Records = new ObservableCollection<Plate>();
                    lastFetchedId = 0;
                }
                return _Records;
            }
            set { SetValue(ref _Records, value); }
        }

        long lastFetchedId = 0;
        private void FillData()
        {
            if (IsLocked)
                return;

            Con.Open();
            var cmd = new SQLiteCommand("SELECT * FROM plates WHERE id>" + lastFetchedId + " ORDER BY id", Con);
            using (var data = cmd.ExecuteReader())
            {
                while (data.Read())
                {
                    Records.Insert(0, new Plate()
                    {
                        Id = data.GetInt64(0),
                        Number = data.GetString(1),
                        Owner = data.GetString(2),
                    });
                }
                lastFetchedId = Records.FirstOrDefault()?.Id ?? 0;
            }
            Con.Close();
        }

        private ImageSource _Detail_Image;
        public ImageSource Detail_Image
        {
            get { return _Detail_Image; }
            set { SetValue(ref _Detail_Image, value); }
        }

        private Dictionary<string, string> _Detail_Records;
        public Dictionary<string, string> Detail_Records
        {
            get { return _Detail_Records; }
            set { SetValue(ref _Detail_Records, value); }
        }


        bool IsLocked = false;
        public void ShowDetails(long id)
        {

            IsLocked = true;
            if (Con.State == System.Data.ConnectionState.Closed)
                Con.Open();
            var cmd = new SQLiteCommand("SELECT image,data FROM plates WHERE id=" + id, Con);
            var data = cmd.ExecuteReader();
            if (data.Read() && data.FieldCount == 2)
            {
                Detail_Image = LoadImage(data[0] as byte[]);
                Detail_Records = JsonConvert.DeserializeObject<Dictionary<string, string>>(data[1].ToString());
            }
            Con.Close();
            IsLocked = false;
        }

        private static BitmapImage LoadImage(byte[] imageData)
        {
            if (imageData == null || imageData.Length == 0) return null;
            var image = new BitmapImage();
            using (var mem = new MemoryStream(imageData))
            {
                mem.Position = 0;
                image.BeginInit();
                image.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
                image.CacheOption = BitmapCacheOption.OnLoad;
                image.UriSource = null;
                image.StreamSource = mem;
                image.EndInit();
            }
            image.Freeze();
            return image;
        }

        public Dictionary<string, string> LoadJson(string file)
        {
            using (StreamReader r = new StreamReader(file))
            {
                string json = r.ReadToEnd();
                return JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
            }
        }
    }
}
