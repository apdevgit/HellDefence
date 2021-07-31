using UnityEngine;
using System.Collections;

public class LivingEntity : MonoBehaviour {

    [SerializeField] private int _maxHealth = 100;
    [SerializeField] private int _health = 100;
    [SerializeField] private int _regeneration = 1;

    private GameObject _damageDealtBillboard;

    private IEnumerator RegenerationCo;

    public int maxHealth
    {
        get { return _maxHealth; }
        set { _maxHealth = value; }
    }

    public float health
    {
        get { return _health; }
    }

    public int regeneration
    {
        get { return _regeneration; }
        set { _regeneration = value; }
    }

    void Awake()
    {
        _damageDealtBillboard = Resources.Load("DamageDealtBillboard") as GameObject;
    }

    void Start()
    {
        StartCoroutine(RegenerationEffect());
    }

    public void IncreaseHealth(int damage)
    {
        if (damage <= 0) { return; }

        if (_health > 0)
        {
            _health += damage;
            if (_health > _maxHealth)
            {
                _health = _maxHealth;
            }
        }
    }

    public void DecreaseHealth(int damage)
    {
        if (damage <= 0) { return; }

        _health -= damage;
        if (_health < 0)
        {
            _health = 0;
        }

        GameObject go = Instantiate(_damageDealtBillboard);
        go.transform.position = transform.position;
        go.transform.Rotate(0, 180, 0);
        go.GetComponent<DamageDealtBillboard>().SetAndReady(damage, new Color(1, 0, 0, 1));
    }

    private IEnumerator RegenerationEffect()
    {
        while (true)
        {
            IncreaseHealth(_regeneration);

            yield return new WaitForSeconds(3f);
        }
    }

    public float GetHealthQuota()
    {
        return ((float)_health / _maxHealth);
    }

    public bool isAlive()
    {
        return _health > 0;
    }

    public bool isDead()
    {
        return _health == 0;
    }
}
