using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class BuffStand : MonoBehaviour {

    private enum BuffType
    {
        Stat,
        Spell,
        FullHeal
    }

    [Header("Visuals")]
    [SerializeField] private GameObject _goldVisual;
    [SerializeField] private GameObject _blueVisual;
    [SerializeField] private GameObject _greenVisual;

    [SerializeField] private GameObject _healVisualEffect;
    private float _healEffectDuration = 3.5f;

    [SerializeField] private GameObject _statVisualEffect;
    private float _statEffectDuration = 3f;

    [SerializeField] private GameObject _spellVisualEffect;
    private float _spellEffectDuration = 3f;

    private GameObject _instantiatedVisual;
    [SerializeField] private Transform _itemPoint;

    [Header("Drop Chances")]
    [Range(0, 100)]
    public float chanceToGiveBuff = 100;
    [Range(0, 100)]
    public float statChance = 45;
    [Range(0, 100)]
    public float spellChance = 5;
    [Range(0, 100)]
    public float fullHealChance = 50;

    private Stat _stat;
    private SpellName _spellName;

    private List<Stat> _statsPool;
    private List<SpellName> _spellPool;

    private bool _hasBuffToGive;
    private BuffType _buffType;

    void Awake()
    {
        _statsPool = new List<Stat>();
        _spellPool = new List<SpellName>();

        InitializeStatPool();
    }

    private void InitializeStatPool()
    {
        _statsPool.Add(new Stat(StatCategory.Speed, StatType.Constant, 2f));
        _statsPool.Add(new Stat(StatCategory.Cooldown, StatType.Quota, .1f));
        _statsPool.Add(new Stat(StatCategory.Damage, StatType.Quota, .1f));
        _statsPool.Add(new Stat(StatCategory.Regeneration, StatType.Constant, 2f));
        _statsPool.Add(new Stat(StatCategory.MaxHealth, StatType.Constant, 50f));
        _statsPool.Add(new Stat(StatCategory.Speed, StatType.Quota, .1f));
    }

    public void GenerateRandomBuff(float duration = Mathf.Infinity)
    {
        if(Random.Range(1, 101) <= chanceToGiveBuff && chanceToGiveBuff != 0)
        {
            ClearBuff();

            if(statChance + spellChance + fullHealChance != 100) { return; }

            int result = Random.Range(1, 101);

            if(result <= statChance && statChance != 0)
            {
                _buffType = BuffType.Stat;
                _stat = _statsPool[Random.Range(0, _statsPool.Count)];
                _instantiatedVisual = Instantiate(_blueVisual, _itemPoint.position, Quaternion.identity) as GameObject;
            }
            else if (result <= statChance + spellChance && spellChance != 0)
            {
                _buffType = BuffType.Spell;
                float probability = Random.Range(0f, 1f);
                if (probability < .25f)
                {
                    _spellName = SpellName.GroundShock;
                }
                else if(probability < .5f)
                {
                    _spellName = SpellName.LavaBeam;
                }
                else if(probability < .75f)
                {
                    _spellName = SpellName.Domestication;
                }
                else
                {
                    _spellName = SpellName.Gravity;
                }

                _instantiatedVisual = Instantiate(_goldVisual, _itemPoint.position, Quaternion.identity) as GameObject;
            }
            else if (result <= statChance + spellChance + fullHealChance && fullHealChance != 0)
            {
                _buffType = BuffType.FullHeal;
                _instantiatedVisual = Instantiate(_greenVisual, _itemPoint.position, Quaternion.identity) as GameObject;
            }

            _hasBuffToGive = true;
            ClearBuffAfterTime(duration);
        }

    }

    void OnTriggerEnter(Collider col)
    {
        if (_hasBuffToGive && col.gameObject.tag == "Player" )
        {
            if(_buffType == BuffType.FullHeal)
            {
                LivingEntity lv = col.gameObject.GetComponent<LivingEntity>();
                lv.IncreaseHealth(lv.maxHealth);

                GameObject visual = Instantiate(_healVisualEffect, col.transform) as GameObject;
                visual.transform.localPosition = Vector3.zero - Vector3.up / 2;
                Destroy(visual, _healEffectDuration);
            }
            else if(_buffType == BuffType.Stat)
            {
                col.gameObject.GetComponent<Stats>().AddStat(new Stat(_stat), 300);

                GameObject visual = Instantiate(_statVisualEffect, col.transform) as GameObject;
                visual.transform.localPosition = Vector3.zero - Vector3.up / 2;
                Destroy(visual, _statEffectDuration);
            }
            else if(_buffType == BuffType.Spell)
            {
                col.gameObject.GetComponent<PlayerSpell>().AddSpecialSpell(_spellName);

                GameObject visual = Instantiate(_spellVisualEffect, col.transform) as GameObject;
                visual.transform.localPosition = Vector3.zero - Vector3.up / 2;
                Destroy(visual, _spellEffectDuration);
            }

            ClearBuff();
        }
    }

    public void ClearBuffAfterTime(float time)
    {
        StartCoroutine(ClearBuffAfterTimeCo(time));
    }

    private IEnumerator ClearBuffAfterTimeCo(float time)
    {
        yield return new WaitForSeconds(time);

        ClearBuff();
    }

    public void ClearBuff()
    {
        _hasBuffToGive = false;
        if (_instantiatedVisual != null)
        {
            Destroy(_instantiatedVisual);
        }
    }

}
