using UnityEngine;
using System.Collections;

[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(AudioSource))]
public class Gravity : Spell
{
    [SerializeField] private float _speed = 7f;
    [SerializeField] private int _damage = 4;
    [SerializeField] private float _damageFrequency = .2f;
    [SerializeField] private float _radius = 4f;
    [SerializeField] private float _maxForce = 15f;
    [SerializeField] private float _lifetime = 4f;
    [SerializeField] private float _distanceFromCaster = 1f;

    private Stats _casterStats;

    private Rigidbody _rg;
    private AudioSource _audioSource;
    private AudioClip _gravitySoundStart;
    private AudioClip _gravitySoundLoop;

    void Awake()
    {
        _casterStats = caster.gameObject.GetComponent<Stats>();

        if (_casterStats != null)
        {
            _damage = (int)((_damage + _casterStats.damageConstant) * (_casterStats.damageQuota + 1));
        }

        _rg = GetComponent<Rigidbody>();

        _audioSource = GetComponent<AudioSource>();
        _gravitySoundStart = Resources.Load("gravitySoundStart") as AudioClip;
        _gravitySoundLoop = Resources.Load("gravitySoundLoop") as AudioClip;

        transform.position = caster.position;
        transform.rotation = caster.rotation;
        transform.Translate(Vector3.forward * _distanceFromCaster + Vector3.up, Space.Self);
    }

    void Start()
    {
        StartCoroutine(ApplyDamage());
        StartCoroutine(ManageSoundPlaying());
        Destroy(this.gameObject, _lifetime);
    }

    void FixedUpdate()
    { 
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, _radius);

        foreach(Collider col in hitColliders)
        {
            if(col.gameObject == caster.gameObject) { continue; }

            RigidbodyWrapper rgw = col.gameObject.GetComponent<RigidbodyWrapper>();
            LivingEntity livingEntity = col.gameObject.GetComponent<LivingEntity>();

            if(livingEntity != null)
            {
                if(!GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
                {
                    continue;
                }
            }

            if (rgw != null)
            {
                Vector3 forceDirection = transform.position - col.transform.position;
                forceDirection.y = 0;
                float distance = forceDirection.magnitude;
                forceDirection.Normalize();

                rgw.AddExternalForce(forceDirection * _maxForce * (distance/_radius));
            }
        }

        _rg.velocity = transform.forward * _speed;
    }
    
    private IEnumerator ManageSoundPlaying()
    {
        _audioSource.PlayOneShot(_gravitySoundStart);
        yield return new WaitForSeconds(_gravitySoundStart.length);
        _audioSource.loop = true;
        _audioSource.clip = _gravitySoundLoop;
        _audioSource.Play();
    }

    private IEnumerator ApplyDamage()
    {
        while (true)
        {
            yield return new WaitForSeconds(_damageFrequency);

            Collider[] hitColliders = Physics.OverlapSphere(transform.position, _radius);

            foreach (Collider col in hitColliders)
            {
                if (col.gameObject == caster.gameObject) { continue; }

                LivingEntity livingEntity = col.GetComponent<LivingEntity>();
                if (livingEntity != null)
                {
                    if(GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
                    {
                        livingEntity.DecreaseHealth(_damage);
                    }
                }
            }
        }
    }

}
