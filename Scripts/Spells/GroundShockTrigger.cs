using UnityEngine;

public class GroundShockTrigger : Spell {

    private int _damage;
    private float _force;
    private float _speed = 10f;
    private float _endScale = 1.6f;

    private GameObject _hitVisualEffect;

    void Awake()
    {
        _hitVisualEffect = Resources.Load("HitVisualEffectRed") as GameObject;
    }

    public void SetVariables(Transform caster, int damage, float force, float speed = 10f)
    {
        this.caster = caster;
        _damage = damage;
        _force = force;
    }

    void Update()
    {
        transform.Translate(Vector3.forward * _speed * Time.deltaTime, Space.Self);
        transform.localScale = Vector3.Lerp(transform.localScale, Vector3.one * _endScale, Time.deltaTime * 2);
    }

    void OnTriggerEnter(Collider col)
    {
        LivingEntity livingEntity = col.gameObject.GetComponent<LivingEntity>();
        RigidbodyWrapper rgw = col.gameObject.GetComponent<RigidbodyWrapper>();

        if(livingEntity != null)
        {
            if(GameDictionary.AreEnemies(col.gameObject.tag, caster.tag))
            {
                livingEntity.DecreaseHealth(_damage);

                if (rgw != null)
                {
                    Vector3 forceDirection = col.transform.position - transform.position;
                    forceDirection.y = 0;

                    rgw.AddExternalForce(_force * forceDirection.normalized);
                }

                GameObject hitVisual = Instantiate(_hitVisualEffect, transform.position, Quaternion.identity) as GameObject;
                Destroy(hitVisual, 1.5f);
                Destroy(gameObject);
            }
            
        }
        else if (rgw != null)
        {
            Vector3 forceDirection = col.transform.position - transform.position;
            forceDirection.y = 0;

            rgw.AddExternalForce(_force * forceDirection.normalized);

            GameObject hitVisual = Instantiate(_hitVisualEffect, transform.position, Quaternion.identity) as GameObject;
            Destroy(hitVisual, 1.5f);
            Destroy(gameObject);
        }

    }

    void OnDestroy()
    {
        Destroy(transform.parent.gameObject);
    }
}
