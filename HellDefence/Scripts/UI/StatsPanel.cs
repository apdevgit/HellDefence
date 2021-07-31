using UnityEngine;
using System.Collections.Generic;

public class StatsPanel : MonoBehaviour {

    [SerializeField] private PlayerNumber _playerNumber;
    [SerializeField] private GameObject _statsFieldPrefab;

    private Stats _playerStats;
    private Dictionary<Stat, GameObject> _existingStatFields;
    private int _statFieldsNumber = 0;

    void Start()
    {
        if (_playerNumber == PlayerNumber.P1)
        {
            _playerStats = GameController.instance.player1Instance.GetComponent<Stats>();
        }
        else if (_playerNumber == PlayerNumber.P2)
        {
            _playerStats = GameController.instance.player2Instance.GetComponent<Stats>();
        }
        
        _existingStatFields = new Dictionary<Stat, GameObject>();
    }
	
	void Update () {

        if (_playerStats.statsPanelFlag)
        {
            foreach (Stat stat in _playerStats.GetAllStats())
            {
                if (!_existingStatFields.ContainsKey(stat))
                {
                    MakeNewStatField(stat);
                }
            }

            foreach (Stat stat in new List<Stat>(_existingStatFields.Keys))
            {
                if (!_playerStats.GetAllStats().Contains(stat))
                {
                    RemoveStatField(stat);
                }
            }

            _playerStats.statsPanelFlag = false;
        }

        // Update times
        foreach (Stat stat in new List<Stat>(_existingStatFields.Keys))
        {
            _existingStatFields[stat].GetComponent<StatField>().SetTimeLeft((int)_playerStats.stats[stat]);
        }
    }

    private void MakeNewStatField(Stat stat)
    {
        GameObject go = Instantiate(_statsFieldPrefab, transform) as GameObject;
        StatField sf = go.GetComponent<StatField>();

        sf.SetStatIcon(Resources.Load(stat.category.ToString(), typeof(Sprite)) as Sprite);
        sf.SetStatInfoText(stat.Description());

        go.transform.localScale = Vector3.one;
        _existingStatFields.Add(stat, go);
        _statFieldsNumber++;
    }

    private void RemoveStatField(Stat stat)
    {
        if (_existingStatFields.ContainsKey(stat))
        {
            Destroy(_existingStatFields[stat]);
            _existingStatFields.Remove(stat);
            _statFieldsNumber--;
        }
    }

}
