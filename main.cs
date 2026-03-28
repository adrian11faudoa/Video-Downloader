using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace VideoDownloader
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void btnBrowseFolder_Click(object sender, EventArgs e)
        {
            using (FolderBrowserDialog fbd = new FolderBrowserDialog())
            {
                if (fbd.ShowDialog() == DialogResult.OK)
                {
                    txtFolder.Text = fbd.SelectedPath;
                }
            }
        }

        private void btnLoadFile_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog ofd = new OpenFileDialog())
            {
                ofd.Filter = "Text Files (*.txt)|*.txt";

                if (ofd.ShowDialog() == DialogResult.OK)
                {
                    txtFile.Text = ofd.FileName;
                }
            }
        }

        private async void btnDownload_Click(object sender, EventArgs e)
        {
            List<string> urls = new List<string>();

            if (!string.IsNullOrWhiteSpace(txtUrl.Text))
                urls.Add(txtUrl.Text.Trim());

            if (!string.IsNullOrWhiteSpace(txtFile.Text))
            {
                try
                {
                    urls.AddRange(File.ReadAllLines(txtFile.Text));
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error reading file:\n{ex.Message}");
                    return;
                }
            }

            if (urls.Count == 0)
            {
                MessageBox.Show("Enter a URL or load a file.");
                return;
            }

            if (string.IsNullOrWhiteSpace(txtFolder.Text))
            {
                MessageBox.Show("Select a folder.");
                return;
            }

            foreach (var url in urls)
            {
                lblStatus.Text = $"Starting: {url}";
                await RunYtDlp(url);
            }

            lblStatus.Text = "All downloads completed!";
            MessageBox.Show("Done!");
        }

        private Task RunYtDlp(string url)
        {
            return Task.Run(() =>
            {
                string folder = txtFolder.InvokeRequired
                    ? (string)txtFolder.Invoke(new Func<string>(() => txtFolder.Text))
                    : txtFolder.Text;

                bool isAudio = radioAudio.InvokeRequired
                    ? (bool)radioAudio.Invoke(new Func<bool>(() => radioAudio.Checked))
                    : radioAudio.Checked;

                string args;

                if (isAudio)
                {
                    args = $"-x --audio-format mp3 --audio-quality 192 -o \"{folder}\\%(title)s_%(id)s.%(ext)s\" {url}";
                }
                else
                {
                    args = $"-f bestvideo+bestaudio -o \"{folder}\\%(title)s_%(id)s.%(ext)s\" {url}";
                }

                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "yt-dlp.exe",
                    Arguments = args,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                Process process = new Process();
                process.StartInfo = psi;

                process.OutputDataReceived += (s, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        UpdateStatus(e.Data);
                    }
                };

                process.ErrorDataReceived += (s, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        UpdateStatus(e.Data);
                    }
                };

                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                process.WaitForExit();
            });
        }

        private void UpdateStatus(string text)
        {
            if (lblStatus.InvokeRequired)
            {
                lblStatus.Invoke(new Action(() => lblStatus.Text = text));
            }
            else
            {
                lblStatus.Text = text;
            }
        }
    }
}
