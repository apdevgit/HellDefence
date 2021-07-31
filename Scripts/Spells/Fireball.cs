using UnityEngine;
using System.Collections;

[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(AudioSource))]
public class Fireball : Spell
{
    [SerializeField] private float _speed = 10f;
    [SerializeField] private int _damage = 10;
    [SerializeField] private float _force = 500f;
    [SerializeField] private float _lifetime = 1.5f;
    [SerializeField] private float _distanceFromCaster = 1f;

    [SerializeField] private Transform _fireballSphere;
    [SerializeField] private GameObject _particle;

    private bool _isAlive;

    private Rigidbody _rg;
    private Stats _casterStats;

    private AudioSource _audioSource;
    private AudioClip _castSound;
    private AudioClip _boomSound;

    private IEnumerator LifeCountdownCR;
    private IEnumerator DestroyAfterLifetime;

    void Awake()
    {
        _rg = GetComponent<Rigidbody>();
        _casterStats = caster.GetComponent<Stats>();
        
        _audioSource = GetComponent<AudioSource>();
        _boomSound = Resources.Load("fireballBoom") as AudioClip;
        _castSound = Resources.Load("fireballCast") as AudioClip;

        if (_casterStats != null)
        {
            _damage = (int)((_damage + _casterStats.damageConstant) * (_casterStats.damageQuota + 1));
        }

       _isAlive = true;

        transform.position = caster.position;
        Vector3 pointToCastTo = caster.GetComponent<PlayerSpell>().pointToCastTo;
        pointToCastTo.y = transform.position.y;

        transform.LookAt(pointToCastTo);
        transform.Translate(Vector3.forward * _distanceFromCaster + Vector3.up, Space.Self);
    }

    void Start () {

        LifeCountdownCR = LifeCountdown();
        _audioSource.PlayOneShot(_castSound);
        StartCoroutine(LifeCountdownCR);
    }

    void FixedUpdate()
    {
        if (_isAlive)
        {
            _rg.velocity = transform.forward * _speed;
            _fireballSphere.transform.Rotate(-350 * Time.deltaTime, 100 * Time.deltaTime, 200 * Time.deltaTime, Space.Self);
            _lifetime -= Time.fixedDeltaTime;
        }
    }

    void OnTriggerEnter(Collider col)
    {
        Spell spell = col.GetComponent<Spell>();

        if (col.isTrigger) { return; }
        if (col.gameObject == caster.gameObject) { return; }
        if ( spell != null) // ignore collision with other casted spells from the caster
        {
            if(spell.caster == caster || !GameDictionary.AreEnemies(spell.caster.tag, caster.tag))
            {
                return;
            }
        }

        Vector3 forceDirection = col.transform.position - transform.position;
        forceDirection.y = 0;
        forceDirection.Normalize();

        LivingEntity livingEntity = col.gameObject.GetComponent<LivingEntity>();
        RigidbodyWrapper rigidbodyWrapper = col.gameObject.GetComponent<RigidbodyWrapper>();

        if (livingEntity != null)
        {
            if (GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
            {
                livingEntity.DecreaseHealth(_damage);
                if (rigidbodyWrapper != null)
                {
                    rigidbodyWrapper.AddExternalForce(forceDirection * _force);
                }

                _isAlive = false;

                StopCoroutine(LifeCountdownCR);
                StartCoroutine(PlaySoundOnHitAndThenDestroy());
            }

        }
        else
        {
            if (rigidbodyWrapper != null)
            {
                rigidbodyWrapper.AddExternalForce(forceDirection * _force);
            }

            _isAlive = false;

            StopCoroutine(LifeCountdownCR);
            StartCoroutine(PlaySoundOnHitAndThenDestroy());
        }

    }

    private void DisableBasicComponents()
    {
        _particle.GetComponent<ParticleSystem>().Stop();
        _fireballSphere.GetComponent<MeshRenderer>().enabled = false;
        GetComponent<SphereCollider>().enabled = false;
        GetComponent<Rigidbody>().detectCollisions = false;
    }

    private IEnumerator LifeCountdown()
    {
        yield return new WaitForSeconds(_lifetime);

        DisableBasicComponents();

        Destroy(this.gameObject, _particle.GetComponent<ParticleSystem>().startLifetime);
    }

    private IEnumerator PlaySoundOnHitAndThenDestroy()
    {
        _isAlive = false;
        DisableBasicComponents();
        _audioSource.PlayOneShot(_boomSound);

        yield return new WaitForSeconds(_boomSound.length);

        Destroy(this.gameObject);
    }
}
