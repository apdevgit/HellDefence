using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class PlayerCooldown : MonoBehaviour
{
    private Stats _playerStats;
    private Dictionary<SpellName, float> _spellCooldowns;

    void Awake()
    {
        _playerStats = GetComponent<Stats>();
        _spellCooldowns = new Dictionary<SpellName, float>();
    }

    public void RegisterSpellCooldown(SpellName spellName)
    {
        if(!_spellCooldowns.ContainsKey(spellName))
        {
            _spellCooldowns.Add(spellName, 0);
        }
    }

    public void UnregisterSpellCooldown(SpellName spellName)
    {
        if (_spellCooldowns.ContainsKey(spellName))
        {
            _spellCooldowns.Remove(spellName);
        }
    }

    public void StartSpellCooldown(SpellName spellName)
    {
        _spellCooldowns[spellName] = GetFinalSpellCooldown(spellName);
        StartCoroutine(ProcessCooldown(spellName));
    }

    private float GetFinalSpellCooldown(SpellName spellName)
    {
        return GameDictionary.GetSpellCooldownTime(spellName) - _playerStats.cooldownConstant -
            GameDictionary.GetSpellCooldownTime(spellName) * _playerStats.cooldownQuota;
    }

    private IEnumerator ProcessCooldown(SpellName spellName)
    {
        float cd = _spellCooldowns[spellName];

        while (cd > 0)
        {
            yield return new WaitForSeconds(.1f);
            cd -= .1f;
            if (_spellCooldowns.ContainsKey(spellName))
            {
                _spellCooldowns[spellName] = cd;
            }
        }

        _spellCooldowns[spellName] = 0;
    }

    public bool HasCooldown(SpellName spellName)
    {
        float spellCurrentCooldown;
        if (_spellCooldowns.TryGetValue(spellName, out spellCurrentCooldown))
        {
            return spellCurrentCooldown == 0;
        }

        return false;
    }

    public float GetSpellCooldownPercentage(SpellName spellName)
    {
        float spellCurrentCooldown;
        if (_spellCooldowns.TryGetValue(spellName, out spellCurrentCooldown))
        {
            return (spellCurrentCooldown / GetFinalSpellCooldown(spellName)) * 100;
        }

        return -1;
    }
}
