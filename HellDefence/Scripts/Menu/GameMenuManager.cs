using UnityEngine;
using UnityEngine.SceneManagement;

public class GameMenuManager : MonoBehaviour {

    [SerializeField] private GameObject gameMenu;
    [SerializeField] private AudioClip _buttonSound;

    private AudioSource _audioSource;
    private bool _menuIsOpen;

    void Start()
    {
        gameMenu.SetActive(false);
        _audioSource = GetComponent<AudioSource>();
    }

    public void OpenMenu()
    {
        PlayClickButtonSound();
        if (!_menuIsOpen)
        {
            Time.timeScale = 0;
            gameMenu.SetActive(true);
            _menuIsOpen = true;
        }
    }

    public void ResumeGame()
    {
        PlayClickButtonSound();
        Time.timeScale = 1;
        gameMenu.SetActive(false);
        _menuIsOpen = false;
    }

    public void GoToMainMenu()
    {
        PlayClickButtonSound();
        Time.timeScale = 1;
        SceneManager.LoadScene("Menu");
    }

    public void ExitGame()
    {
        PlayClickButtonSound();
        Application.Quit();
    }

    private void PlayClickButtonSound()
    {
        if (_audioSource != null)
        {
            _audioSource.PlayOneShot(_buttonSound);
        }
    }
}
