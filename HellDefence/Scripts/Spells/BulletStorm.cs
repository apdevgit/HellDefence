using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class BulletStorm : Spell {

    [SerializeField] private AudioClip _emissionSound;
    [SerializeField] private int _damage = 12;

    private ParticleSystem _particleSystem;
    private ParticleCollisionEvent[] _collisionEvents;
    private AudioSource _audioSource;

    private Stats _casterStats;
    private int _numberOfParticles;
    private float _lifetime = 5f;

    void Awake()
    {
        _casterStats = caster.GetComponent<Stats>();
        if (_casterStats != null)
        {
            _damage = (int)((_damage + _casterStats.damageConstant) * (_casterStats.damageQuota + 1));
        }

        transform.position = caster.GetComponent<PlayerSpell>().pointToCastTo + Vector3.up * 10;
        Destroy(gameObject, 5f);
    }

	void Start()
    {
        _particleSystem = GetComponent<ParticleSystem>();
        _collisionEvents = new ParticleCollisionEvent[8];
        _audioSource = GetComponent<AudioSource>();
        _numberOfParticles = _particleSystem.particleCount;
    }

    void Update()
    {
        if(_numberOfParticles < _particleSystem.particleCount)
        {
            _audioSource.PlayOneShot(_emissionSound);
        }

        _numberOfParticles = _particleSystem.particleCount;
    }

    void OnParticleCollision(GameObject go)
    {
        int collCount = _particleSystem.GetSafeCollisionEventSize();

        if(collCount > _collisionEvents.Length)
        {
            _collisionEvents = new ParticleCollisionEvent[collCount];
        }

        int eventCount = _particleSystem.GetCollisionEvents(go, _collisionEvents);
        
        for(int i = 0; i < eventCount; i++)
        {
            Vector3 collisionPoint = _collisionEvents[i].intersection;

            Collider[] hitColliders = Physics.OverlapSphere(collisionPoint, 3.6f);

            foreach( Collider hitCol in hitColliders)
            {
                LivingEntity lve = hitCol.gameObject.GetComponent<LivingEntity>();

                if(lve != null)
                {
                    if(GameDictionary.AreEnemies(caster.tag, hitCol.gameObject.tag))
                    {
                        lve.DecreaseHealth(_damage);
                    }
                }
            }
        }

    }

}
