using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace Data_Viewer.Common
{
//#pragma warning disable CS0067
    public class DelegateCommand : ICommand
    {
        private Action<object> Action;
        private Predicate<object> canExec;

        public event EventHandler CanExecuteChanged
        {
            add { CommandManager.RequerySuggested += value; }
            remove { CommandManager.RequerySuggested -= value; }
        }

        public DelegateCommand(Action<object> action,Predicate<object> canexec = null)
        {
            if (action != null)
                this.Action = action;
            if (canexec != null)
                this.canExec = canexec;
        }
        
        public bool CanExecute(object parameter)
        {
            if (this.canExec != null)
            {
                return canExec.Invoke(parameter);
            }
            return true;
        }

        public void Execute(object parameter)
        {
            if (this.Action != null)
                Action.Invoke(parameter);
        }
    }
}
