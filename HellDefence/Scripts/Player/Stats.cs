using UnityEngine;
using System.Collections.Generic;

public class Stats : MonoBehaviour
{
    private LivingEntity _livingEntity;
    private RigidbodyWrapper _rgw;

    [HideInInspector]
    public bool statsPanelFlag;

    public int baseMaxHealth { get; private set; }
    public int baseRegeneration { get; private set; }
    public float baseSpeed { get; private set; }
    public float baseMass { get; private set; }

    public int maxHealth { get; private set; }
    public int regeneration { get; private set; }
    public float speed { get; private set; }
    public float damageConstant { get; private set; }
    public float damageQuota { get; private set; }
    public float mass { get; private set; }
    public float cooldownConstant { get; private set; }
    public float cooldownQuota { get; private set; }

    private Dictionary<Stat, float> _stats;

    public Dictionary<Stat, float> stats
    {
        get { return _stats; }
    }

    void Awake()
    {
        _rgw = GetComponent<RigidbodyWrapper>();
        _livingEntity = GetComponent<LivingEntity>();

        _stats = new Dictionary<Stat, float>();

        InitializeData();
    }

    void Start()
    {
        StatInit();
        statsPanelFlag = true;
    }

    void Update()
    {
        List<Stat> toDelete = new List<Stat>();
        bool thereAreChanges = false;

        foreach(Stat stat in new List<Stat>(_stats.Keys))
        {
            if (_stats[stat] > 0)
            {
                _stats[stat] -= Time.deltaTime;
            }
            else if(_stats[stat] != -1)
            {
                toDelete.Add(stat);
                if (thereAreChanges == false)
                {
                    thereAreChanges = true;
                }
            }
        }

        foreach(Stat stat in toDelete)
        {
            _stats.Remove(stat);
        }

        if (thereAreChanges)
        {
            CalculateStats();
        }
    }

    public void InitializeData()
    {
        baseMaxHealth = _livingEntity.maxHealth;
        baseRegeneration = _livingEntity.regeneration;
        baseSpeed = _rgw.speed;
        baseMass = _rgw.mass;
    }

    public void StatInit()
    {
        maxHealth = baseMaxHealth;
        regeneration = baseRegeneration;
        speed = baseSpeed;
        damageConstant = 0;
        damageQuota = 0;
        mass = baseMass;
        cooldownConstant = 0;
        cooldownQuota = 0;
    }

    public void AddStat(Stat stat, float lifetime = -1f)
    {
        _stats.Add(stat, lifetime);

        CalculateStats();
    }

    public void Remove(Stat stat)
    {
        _stats.Remove(stat);

        CalculateStats();
    }

    public void RemoveAllStats()
    {
        _stats = new Dictionary<Stat, float>();

        CalculateStats();
    }

    public List<Stat> GetAllStats()
    {
        return new List<Stat>(_stats.Keys);
    }

    public void CalculateStats()
    {
        StatInit();
        foreach (Stat stat in _stats.Keys)
        {
            if (stat.type == StatType.Constant)
            {
                switch (stat.category)
                {
                    case StatCategory.MaxHealth:
                        maxHealth += (int)stat.factorValue;
                        break;

                    case StatCategory.Regeneration:
                        regeneration += (int)stat.factorValue;
                        break;

                    case StatCategory.Speed:
                        speed += stat.factorValue;
                        break;

                    case StatCategory.Damage:
                        damageConstant += stat.factorValue;
                        break;

                    case StatCategory.Mass:
                        mass += stat.factorValue;
                        break;

                    case StatCategory.Cooldown:
                        cooldownConstant += stat.factorValue;
                        break;
                }
            }
        }

        foreach (Stat stat in _stats.Keys)
        {
            if (stat.type == StatType.Quota)
            {
                switch (stat.category)
                {
                    case StatCategory.MaxHealth:
                        maxHealth += (int)(maxHealth * stat.factorValue);
                        break;

                    case StatCategory.Regeneration:
                        regeneration += (int)(regeneration * stat.factorValue);
                        break;

                    case StatCategory.Speed:
                        speed += speed * stat.factorValue;
                        break;

                    case StatCategory.Damage:
                        damageQuota += stat.factorValue;
                        break;

                    case StatCategory.Mass:
                        mass += mass * stat.factorValue;
                        break;

                    case StatCategory.Cooldown:
                        cooldownQuota += stat.factorValue;
                        break;
                }
            }
        }

        ReApplyVariables();
        statsPanelFlag = true;
    }

    private void ReApplyVariables()
    {
        _livingEntity.maxHealth = maxHealth;
        _livingEntity.regeneration = regeneration;
        _rgw.mass = mass;
        _rgw.speed = speed;
    }
}
