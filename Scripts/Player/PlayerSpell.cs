using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class PlayerSpell : MonoBehaviour
{
    private PlayerCooldown _playerCooldown;
    private PlayerAnimation _playerAnimation;
    private RigidbodyWrapper _rgw;

    [HideInInspector]
    public bool spellBarFlag;

    private SpellName _selectedSpell;
    public bool spellOnCast { get; private set; }
    private Vector3 _pointToCastTo;

    [SerializeField] private List<SpellName> _spells;
    private SpellName _specialSpell = SpellName.None;

    private IEnumerator currentCastSelectedSpell;
    private IEnumerator rotateOnCast;

    public SpellName specialSpell
    {
        get { return _specialSpell; }
    }

    public Vector3 pointToCastTo
    {
        get { return _pointToCastTo; }
        set { _pointToCastTo = value; }
    }

    void Awake()
    {
        _playerCooldown = GetComponent<PlayerCooldown>();
        _playerAnimation = GetComponent<PlayerAnimation>();
        _rgw = GetComponent<RigidbodyWrapper>();

        selectedSpell = SpellName.None;
        pointToCastTo = Vector3.zero;
        spellOnCast = false;
        currentCastSelectedSpell = null;
        rotateOnCast = null;

        foreach( SpellName spellName in _spells)
        {
            _playerCooldown.RegisterSpellCooldown(spellName);
        }
        spellBarFlag = true;
    }

    public SpellName selectedSpell
    {
        get { return _selectedSpell; }
        private set
        {
            _selectedSpell = value;
        }
    }

    void SpellIsOnCast(bool status, bool castCancelOccured = false)
    {
        spellOnCast = status;

        if (castCancelOccured)
        {
            _playerAnimation.OnCastCancel();
        }
        else
        {
            _playerAnimation.SetIsCasting(status);
        }
    }

    public void CancelCast()
    {
        if (currentCastSelectedSpell != null)
        {
            StopCoroutine(currentCastSelectedSpell);
            if (rotateOnCast != null)
            {
                StopCoroutine(rotateOnCast);
            }
            SpellIsOnCast(false, true);
        }
    }

    public void CastSpell(SpellName spellName)
    {
        GameObject spellObject;
        
        if (_spells.Contains(spellName) || spellName == _specialSpell
            && spellName != SpellName.None && _playerCooldown.HasCooldown(spellName))
        {
            spellObject = GameDictionary.GetSpellGameObject(spellName);
            if (spellObject != null)
            {
                currentCastSelectedSpell = StartSpellCast(spellName);
                StartCoroutine(currentCastSelectedSpell);
                if(GameDictionary.GetSpellType(spellName) == SpellType.NormalCast)
                {
                    rotateOnCast = StartRotateOnCast(spellName);
                    StartCoroutine(rotateOnCast);
                }
            }
        }
    }

    private IEnumerator StartSpellCast(SpellName spellName)
    {
        SpellIsOnCast(true);

        yield return new WaitForSeconds(GameDictionary.GetSpellCastingTime(spellName));

        if (rotateOnCast != null)
        {
            StopCoroutine(rotateOnCast);
        }
        currentCastSelectedSpell = null;
        rotateOnCast = null;
        SpellIsOnCast(false);

        _playerCooldown.StartSpellCooldown(spellName);

        GameObject spell = GameDictionary.GetSpellGameObject(spellName);
        spell.SetActive(false);
        GameObject castedSpell = Instantiate(spell);
        castedSpell.GetComponent<Spell>().caster = transform;
        castedSpell.SetActive(true);
        
    }

    private IEnumerator StartRotateOnCast(SpellName spellName)
    {
        float timeLimit = GameDictionary.GetSpellCastingTime(spellName);
        
        Vector3 castDestination = pointToCastTo - transform.position;
        castDestination.y = 0;

        Quaternion startRotation = transform.rotation;
        Quaternion rotation = Quaternion.LookRotation(castDestination);

        for (float t = 0; t < 1;)
        {
            t = Mathf.Min(t + Time.deltaTime / timeLimit, 1);
            transform.rotation = Quaternion.Lerp(startRotation, rotation, t);
            yield return null;
        }

    }

    public bool HasSpell(SpellName spellName)
    {
        return _spells.Contains(spellName);
    }

    public void SelectSpell(SpellName spellName)
    {
        if(spellName == SpellName.None)
        {
            selectedSpell = spellName;
            return;
        }
        if(_playerCooldown.HasCooldown(spellName))
        {
            selectedSpell = spellName;
        }
    }

    public void AddSpell(SpellName spellName)
    {
        _spells.Add(spellName);
        _playerCooldown.RegisterSpellCooldown(spellName);
        spellBarFlag = true;
    }

    public void RemoveSpell(SpellName spellName)
    {
        if (_spells.Contains(spellName))
        {
            _spells.Remove(spellName);
            spellBarFlag = true;
        }
    }

    public void RemoveSpecialSpell()
    {
        _playerCooldown.UnregisterSpellCooldown(_specialSpell);
        _specialSpell = SpellName.None;
        spellBarFlag = true;
    }

    public void AddSpecialSpell(SpellName spellName)
    {
        _specialSpell = spellName;
        _playerCooldown.RegisterSpellCooldown(spellName);
        spellBarFlag = true;
    }
    
    public bool HasSpecialSpell()
    {
        return _specialSpell != SpellName.None;
    }

    public List<SpellName> GetPlayerSpells(bool includingSpecialSpell = false)
    {
        if (includingSpecialSpell && _specialSpell != SpellName.None)
        {
            List<SpellName> result = new List<SpellName>(_spells);
            result.Add(_specialSpell);
            return result;
        }

        return new List<SpellName>(_spells);
    }
}

