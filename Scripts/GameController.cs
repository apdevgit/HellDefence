using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class GameController : MonoBehaviour {

    private enum GameState
    {
        BeforeWaveSetToSpawn,
        ReadyToStartWaveSpawn,
        WaveIsSpawning,
        WaveIsSpawned,
        WaveIsDead,
        GameWon,
        None
    }

    public static GameController instance;

    [SerializeField] private Transform gameWorld;

    [SerializeField] private GameObject _player2Canvas;

    [Header("Players")]
    [SerializeField] private GameObject player1;
    [SerializeField] private GameObject player2;

    [Header("Mobs")]
    [SerializeField] private GameObject[] _mobs;

    [Header("Mob Spawn Points")]
    [SerializeField] private Transform[] _mobSpawnPoints;

    [Header("Player Spawn Points")]
    [SerializeField] private Transform _player1SpawnPoint;
    [SerializeField] private Transform _player2SpawnPoint;

    [Header("Buff Stands")]
    [SerializeField] private BuffStand[] _buffStands;

    [Header("Entrance Gate Collider")]
    [SerializeField] private Transform _EntranceGateCollider;

    [Header("Notifications Text")]
    [SerializeField] private Text _waveText;
    [SerializeField] private Text _gameOverText;
    [SerializeField] private Text _winText;
    [SerializeField] private Text _waveNumberText;
    [SerializeField] private Text _fpsText;
    [SerializeField] private AudioClip _winningSound;
    [SerializeField] private GameObject _returnAfterWinButton;

    private AudioSource _audioSource;

    private Vector3 _entranceGateColliderStartScale;
    private Vector3 _entranceGateColliderEndScale;

    public GameObject player1Instance { get; private set; }
    public GameObject player2Instance { get; private set; }

    private int _currentWaveNumber;
    private List<GameObject> _currentWaveMobs;

    private float counter = 0;
    private bool _gameWon;

    private GameState _gameState = GameState.None;
    private GameState _previousGameState = GameState.None;

	void Awake () {

        instance = this;
        _currentWaveNumber = 1;
        _waveNumberText.text = "Wave " + _currentWaveNumber.ToString();
        _currentWaveMobs = new List<GameObject>();

        _audioSource = GetComponent<AudioSource>();

        _returnAfterWinButton.SetActive(false);
        _player2Canvas.SetActive(false);

        _waveText.color = new Color(_waveText.color.r, _waveText.color.g, _waveText.color.b, 0);

        player1Instance = Instantiate(player1, _player1SpawnPoint.position, Quaternion.identity) as GameObject;
        if (PlayersNumber.number == 2)
        {
            player2Instance = Instantiate(player2, _player2SpawnPoint.position, Quaternion.identity) as GameObject;
            _player2Canvas.SetActive(true);
        }
        else
        {
            player2Instance = null;
        }

        _entranceGateColliderStartScale = _EntranceGateCollider.localScale;
        _entranceGateColliderEndScale = new Vector3(_EntranceGateCollider.localScale.x, _EntranceGateCollider.localScale.y, 52);

        StartCoroutine(EnableTheWorld());
    }

    void Update()
    {
        counter += 1; //fps

        if(_gameState == GameState.BeforeWaveSetToSpawn && _gameState != _previousGameState)
        {
            _previousGameState = _gameState;
            StartCoroutine(SetGameStateInTime(GameState.ReadyToStartWaveSpawn, 5f));
        }
        else if(_gameState == GameState.ReadyToStartWaveSpawn && _gameState != _previousGameState)
        {
            _previousGameState = _gameState;
            StartCoroutine(ShowWaveNumber(_currentWaveNumber));
            StartCoroutine(SendNextWave());
            RefreshBuffStands();
            _gameState = GameState.WaveIsSpawning;
        }
        else if(_gameState == GameState.WaveIsSpawning && _gameState != _previousGameState)
        {
            _previousGameState = _gameState;
        }
        else if(_gameState == GameState.WaveIsSpawned && _gameState != _previousGameState)
        {
            _previousGameState = _gameState;
            StartCoroutine(CheckIfWaveIsDeadPerTime(3));
        }
        else if(_gameState == GameState.WaveIsDead && _gameState != _previousGameState)
        {
            CheckAndUpdateHighScore(_currentWaveNumber);
            _previousGameState = _gameState;
            _gameState = GameState.BeforeWaveSetToSpawn;
            ClearPlayersSpecialSpell();
            _currentWaveNumber++;
            _waveNumberText.text = "Wave " + _currentWaveNumber.ToString();
        }
        else if (_gameWon && _gameState != _previousGameState)
        {
            _previousGameState = _gameState;
            StartCoroutine(ShowGameWinAndReturn());
        }
    }

    private IEnumerator ManageFpsCount()
    {
        while (true)
        {
            _fpsText.text = "FPS: " + counter.ToString();
            counter = 0;
            yield return new WaitForSeconds(1);
        }
    }

    public IEnumerator EnableTheWorld()
    {
        yield return new WaitForSeconds(0);

        yield return new WaitForSeconds(0);

        gameWorld.gameObject.SetActive(true);
        InitializeBuffStands();

        _gameState = GameState.BeforeWaveSetToSpawn;

        StartCoroutine(ManageFpsCount());
        StartCoroutine(CheckForGameOver());
    }

    private IEnumerator SendNextWave()
    {
        yield return new WaitForSeconds(3);

        _EntranceGateCollider.localScale = _entranceGateColliderStartScale;

        _currentWaveMobs = new List<GameObject>();

        foreach (GameObject go in CreateWaveFromData(_currentWaveNumber))
        {
            GameObject newMob = 
                Instantiate(go, _mobSpawnPoints[Random.Range(0, _mobSpawnPoints.Length)].position, Quaternion.identity) as GameObject;

            if(PlayersNumber.number == 2)
            {
                LivingEntity lv = newMob.GetComponent<LivingEntity>();
                lv.maxHealth = (int) (lv.maxHealth * 1.8);
                lv.IncreaseHealth(lv.maxHealth);
            }

            newMob.GetComponent<MobBehaviour>().SetDestination(new Vector3(Random.Range(-5f, 5f), 0, Random.Range(-5f, 5f)));

            _currentWaveMobs.Add(newMob);

            yield return new WaitForSeconds(.8f);
        }

        float timePast = 0;

        while(timePast < 3f)
        {
            _EntranceGateCollider.localScale= Vector3.Lerp(_entranceGateColliderStartScale, _entranceGateColliderEndScale, timePast / 3);

            timePast += Time.deltaTime;
            yield return null;
        }

        _previousGameState = _gameState;
        _gameState = GameState.WaveIsSpawned;
    }

    private List<GameObject> CreateRandomMobWave(float mobsNumber)
    {
        List<GameObject> mobList = new List<GameObject>();

        for(int i = 0; i < mobsNumber; i++)
        {
            mobList.Add(_mobs[Random.Range(0, _mobs.Length)]);
        }

        return mobList;
    }

    private IEnumerator ShowWaveNumber(float waveNumber)
    {
        _waveText.text = "Wave " + waveNumber;

        float timeCount = 0;

        while(timeCount < 3)
        {
            timeCount += Time.deltaTime;
            _waveText.color = new Color(_waveText.color.r, _waveText.color.g, _waveText.color.b, timeCount / 3);
            yield return null;
        }

        yield return new WaitForSeconds(3);

        timeCount = 0;

        while (timeCount < 3)
        {
            timeCount += Time.deltaTime;
            _waveText.color = new Color(_waveText.color.r, _waveText.color.g, _waveText.color.b, 1 - timeCount / 3);
            yield return null;
        }

    }

    private IEnumerator ShowGameOver()
    {
        _gameOverText.text = "Game Over";

        float timeCount = 0;

        while (timeCount < 3)
        {
            timeCount += Time.deltaTime;
            _gameOverText.color = new Color(_gameOverText.color.r, _gameOverText.color.g, _gameOverText.color.b, timeCount / 3);
            yield return null;
        }

    }

    private IEnumerator ShowGameWinAndReturn()
    {
        _winText.text = "Congratulations\nYou have won\nthe game!";

        float timeCount = 0;

        _audioSource.Stop();
        _audioSource.clip = _winningSound;
        _audioSource.Play();

        while (timeCount < 3)
        {
            timeCount += Time.deltaTime;
            _winText.color = new Color(_winText.color.r, _winText.color.g, _winText.color.b, timeCount / 3);
            yield return null;
        }

        yield return new WaitForSeconds(2);

        _returnAfterWinButton.SetActive(true);

    }

    private bool CheckIfWaveIsDead()
    {
        if (_currentWaveMobs.Count > 0)
        {
            foreach (GameObject mob in _currentWaveMobs)
            {
                if (mob != null)
                {
                    if (GameDictionary.AreEnemies("Player", mob.tag))
                    {
                        return false;
                    }
                }
            }

            return true;
        }

        return false;
    }

    private IEnumerator SetGameStateInTime(GameState gameState, float time)
    {
        yield return new WaitForSeconds(time);

        _previousGameState = _gameState;
        _gameState = gameState;
    }

    private IEnumerator CheckIfWaveIsDeadPerTime(float time)
    {
        while (true)
        {
            if (CheckIfWaveIsDead())
            {
                if (_currentWaveNumber == 15)
                {
                    _gameWon = true;
                    _previousGameState = _gameState;
                    _gameState = GameState.GameWon;
                }
                else
                {
                    _previousGameState = _gameState;
                    _gameState = GameState.WaveIsDead;
                }
                break;
            }

            yield return new WaitForSeconds(time);
        }
    }

    private IEnumerator CheckForGameOver()
    {
        while (true)
        {
            yield return new WaitForSeconds(5);

            if (player2Instance == null)
            {
                if (player1Instance.GetComponent<LivingEntity>().isDead())
                {
                    break;
                }
            }
            else
            {
                if (player1Instance.GetComponent<LivingEntity>().isDead() &&
                    player2Instance.GetComponent<LivingEntity>().isDead() )
                {
                    break;
                }
            }
        }

        StartCoroutine(ShowGameOver());

        yield return new WaitForSeconds(10f);

        SceneManager.LoadScene("Menu");
    }

    private void RefreshBuffStands()
    {
        foreach(BuffStand stand in _buffStands)
        {
            if (stand.gameObject.activeSelf)
            {
                stand.GenerateRandomBuff();
            }
        }
    }

    private void ClearPlayersSpecialSpell()
    {
        if(player1Instance != null)
        {
            player1Instance.GetComponent<PlayerSpell>().RemoveSpecialSpell();
        }
        if (player2Instance != null)
        {
            player2Instance.GetComponent<PlayerSpell>().RemoveSpecialSpell();
        }
    }

    private GameObject GetMobByName(string name)
    {
        foreach(GameObject go in _mobs)
        {
            if(go.name.Equals(name.Trim()))
            {
                return go;
            }
        }

        return null;
    }

    private List<GameObject> CreateWaveFromData(int waveNum)
    {
        List<GameObject> mobList = new List<GameObject>();
        TextAsset waves = Resources.Load("waves") as TextAsset;
        string[] wavesText = waves.text.Split('\n');

        bool startReadingWave = false;

        foreach(string line in wavesText)
        {
            if (line.Contains("[wave" + waveNum.ToString() + ']'))
            {
                startReadingWave = true;
            }
            
            if (startReadingWave)
            {
                if (line.StartsWith("+"))
                {
                    if (GetMobByName(line.Substring(1, line.Length - 1)) != null)
                    {
                        mobList.Add(GetMobByName(line.Substring(1, line.Length - 1)));
                    }
                }
            }

            if (line.Contains("[]") && startReadingWave)
            {
                break;
            }
        }

        return mobList;
    }

    private void InitializeBuffStands()
    {
        if(PlayersNumber.number == 1)
        {
            _buffStands[4].gameObject.SetActive(false);
            _buffStands[5].gameObject.SetActive(false);
        }
        else
        {
            _buffStands[4].gameObject.SetActive(true);
            _buffStands[5].gameObject.SetActive(true);
        }
    }

    private void CheckAndUpdateHighScore(int score)
    {
        if(score > PlayerPrefs.GetInt("highscore"))
        {
            PlayerPrefs.SetInt("highscore", score);
            PlayerPrefs.Save();
        }
    }
}
