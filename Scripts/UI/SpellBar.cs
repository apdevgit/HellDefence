using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

[RequireComponent(typeof(RectTransform))]
public class SpellBar : MonoBehaviour
{
    [SerializeField] private PlayerNumber _playerNumber;

    private PlayerSpell _playerSpell;
    private Dictionary<SpellName, GameObject> _existingSpellButtons;
    private int _spellButtonsNumber;

    void Start()
    {
        if (_playerNumber == PlayerNumber.P1)
        {
            _playerSpell = GameController.instance.player1Instance.GetComponent<PlayerSpell>();
        }
        else if(_playerNumber == PlayerNumber.P2)
        {
            _playerSpell = GameController.instance.player2Instance.GetComponent<PlayerSpell>();
        }

        _existingSpellButtons = new Dictionary<SpellName, GameObject>();

        _spellButtonsNumber = 0;
    }

    void Update()
    {
        if(_playerSpell.spellBarFlag == true)
        {

            foreach(SpellName spellName in _playerSpell.GetPlayerSpells())
            {
                if(!_existingSpellButtons.ContainsKey(spellName))
                {
                    MakeNewSpellButton(spellName);
                }
            }

            foreach(SpellName spellName in new List<SpellName>(_existingSpellButtons.Keys))
            {
                if (!_playerSpell.GetPlayerSpells().Contains(spellName) && spellName != _playerSpell.specialSpell)
                {
                    RemoveButton(spellName);
                }
            }

            if (_playerSpell.HasSpecialSpell())
            {
                if (!_existingSpellButtons.ContainsKey(_playerSpell.specialSpell))
                {
                    MakeNewSpellButton(_playerSpell.specialSpell);
                }
            }

            _playerSpell.spellBarFlag = false;
        }
    }

    private void RemoveButton(SpellName spellName)
    {
        if (_existingSpellButtons.ContainsKey(spellName))
        {
            Destroy(_existingSpellButtons[spellName]);
            _existingSpellButtons.Remove(spellName);
            _spellButtonsNumber--;
        }
    }

    private void MakeNewSpellButton(SpellName spellName)
    {
        GameObject go = new GameObject();
        go.SetActive(false);
        go.AddComponent<RectTransform>();
        go.AddComponent<Image>();
        
        SpellButtonBehaviour spellBB = go.AddComponent<SpellButtonBehaviour>();
        spellBB.representedSpell = spellName;
        spellBB.SetTheNumberOfThePlayer(_playerNumber);
        go.transform.SetParent(transform, false);
        go.name = "SpellIcon: " + spellName;
        go.SetActive(true);

        _existingSpellButtons.Add(spellName, go);
        _spellButtonsNumber += 1;
    }
    
}
