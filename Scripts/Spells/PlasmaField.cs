using UnityEngine;
using System.Collections;

[RequireComponent(typeof(AudioSource))]
public class PlasmaField : Spell {

    [SerializeField] private GameObject _destroyEffectParticle;
    [SerializeField] private AudioClip _enableSound;

    private AudioSource _audioSource;
    private Transform _child;
    private float _maxSize = 5;
    private float _lifetime = 7;

    void Start()
    {
        _child = transform.GetChild(0);

        _audioSource = GetComponent<AudioSource>();

        transform.position = caster.transform.position;
        transform.rotation = Quaternion.identity;

        StartCoroutine(Grow());
        StartCoroutine(FadeOut(_lifetime));

        _audioSource.PlayOneShot(_enableSound);
    }

    void Update()
    {
        transform.position = caster.transform.position;
    }

    private IEnumerator Grow()
    {
        float counter = 1;

        while (counter < _maxSize)
        {
            counter += (_maxSize / .4f) * Time.deltaTime;
            transform.localScale = Vector3.one * counter;
            _child.localScale = Vector3.one * counter;

            yield return null;
        }
    }

    private IEnumerator FadeOut(float delay)
    {
        yield return new WaitForSeconds(delay);

        float counter = _maxSize;

        while (counter > 0)
        {
            counter -= (_maxSize / .2f) * Time.deltaTime;
            transform.localScale = Vector3.one * counter;
            _child.localScale = Vector3.one * counter;

            yield return null;
        }

        Destroy(this.gameObject);
    }

    void OnTriggerEnter(Collider col)
    {
        if (col.gameObject.GetComponent<ThrowingObject>() != null)
        {
            if (GameDictionary.AreEnemies(caster.tag, col.GetComponent<ThrowingObject>().caster.tag))
            {
                GameObject go = Instantiate(_destroyEffectParticle);
                go.transform.position = col.transform.position;
                Destroy(col.gameObject);
                Destroy(go, 3f);
            }
        }
        else if (col.gameObject.GetComponent<Spell>() != null)
        {
            if (GameDictionary.AreEnemies(caster.tag, col.gameObject.GetComponent<Spell>().caster.gameObject.tag))
            {
                GameObject go = Instantiate(_destroyEffectParticle, col.transform.position, Quaternion.identity) as GameObject;
                Destroy(col.gameObject);
                Destroy(go, 3f);
            }
        }

    }

    void OnTriggerStay(Collider col)
    {
        if (GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
        {
            Vector3 forceDirection = col.transform.position - transform.position;
            forceDirection.y = 0;
            forceDirection.Normalize();
            col.gameObject.GetComponent<RigidbodyWrapper>().AddExternalForce(forceDirection * 100);
        }
    }

    void OnTriggerExit(Collider col)
    {
        if (col.gameObject.GetComponent<LivingEntity>() != null && col.gameObject.GetComponent<LivingEntity>() != null)
        {
            if (GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
            {
                col.gameObject.GetComponent<RigidbodyWrapper>().EraseExternalForces();
            }
        }

    }

}

