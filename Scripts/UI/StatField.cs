using UnityEngine;
using UnityEngine.UI;

public class StatField : MonoBehaviour {

    [SerializeField] private Image _statImage;
    [SerializeField] private Text _statInfoText;
    [SerializeField] private Text _timeLeftText;

    public void SetStatIcon(Sprite icon)
    {
        _statImage.sprite = icon;
    }

    public void SetStatInfoText(string info)
    {
        _statInfoText.text = info;
    }

    public void SetTimeLeft(int seconds)
    {
        if (seconds == -1)
        {
            _timeLeftText.text = " INF";
        }
        else if (seconds < 60)
        {
            _timeLeftText.text = seconds.ToString() + " secs";
        }
        else
        {
            _timeLeftText.text = (seconds / 60).ToString() + " mins";
        }
    }

}
