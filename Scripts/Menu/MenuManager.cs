using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class MenuManager : MonoBehaviour {

    [SerializeField] private GameObject _mainMenu;
    [SerializeField] private GameObject _howToPlay;
    [SerializeField] private GameObject _controls;

    [SerializeField] private GameObject _onePlayerSelectedSign;
    [SerializeField] private GameObject _twoPlayersSelectedSign;

    [SerializeField] private AudioClip _buttonSound;

    [SerializeField] private Text _highScore;

    private AudioSource _audioSource;
    private int playersNum;


    void Start()
    {
        SelectOnePlayer();
        GoToMainMenu();
        ReadAndSetHighScore();
        _audioSource = GetComponent<AudioSource>();
    }

    public void GoToMainMenu()
    {
        PlayClickButtonSound();
        _mainMenu.SetActive(true);
        _howToPlay.SetActive(false);
        _controls.SetActive(false);
    }

    public void GoToHowToPlay()
    {
        PlayClickButtonSound();
        _mainMenu.SetActive(false);
        _howToPlay.SetActive(true);
        _controls.SetActive(false);
    }

    public void GoToControls()
    {
        PlayClickButtonSound();
        _mainMenu.SetActive(false);
        _howToPlay.SetActive(false);
        _controls.SetActive(true);
    }

    public void StartGame()
    {
        PlayClickButtonSound();
        PlayersNumber.number = playersNum;
        SceneManager.LoadScene("Gameplay");
    }

    public void SelectOnePlayer()
    {
        PlayClickButtonSound();
        playersNum = 1;
        _onePlayerSelectedSign.SetActive(true);
        _twoPlayersSelectedSign.SetActive(false);
    }

    public void SelectTwoPlayers()
    {
        PlayClickButtonSound();
        playersNum = 2;
        _onePlayerSelectedSign.SetActive(false);
        _twoPlayersSelectedSign.SetActive(true);
    }

    public void OnExit()
    {
        PlayClickButtonSound();
        Application.Quit();
    }

    private void PlayClickButtonSound()
    {
        if(_audioSource != null)
        {
            _audioSource.PlayOneShot(_buttonSound);
        }
    }

    private void ReadAndSetHighScore()
    {
        
        if (!PlayerPrefs.HasKey("highscore"))
        {
            PlayerPrefs.SetInt("highscore", 0);
        }
        
        if(PlayerPrefs.GetInt("highscore") > 0)
        {
            _highScore.text = "Highscore: Wave " + PlayerPrefs.GetInt("highscore");
        }
        else
        {
            _highScore.text = "";
        }
        
        PlayerPrefs.Save();
    }
}
