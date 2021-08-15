using UnityEngine;

public class ThrowingObject : MonoBehaviour {

    private GameObject _caster;
    private float _rotationSpeed = 5f;
    private int _damage = 10;
    private float _hitForce = 300f;
    private float _speed = 20f;
    private Vector3 _direction;
    private float _lifetime = 4f;
    private Vector3 _target;

    private Rigidbody _rg;

    private GameObject _hitVisualEffect;

    public GameObject caster
    {
        get { return _caster; }
    }

	void Awake()
    {
        _rg = GetComponent<Rigidbody>();
        _hitVisualEffect = Resources.Load("HitVisualEffect") as GameObject;

        if (_target == null)
        {
            _direction = transform.forward;
        }
    }

    void Start()
    {
        _direction = _target - transform.position;
        _direction.y = 0;

        _rg.velocity = _direction.normalized * _speed;
        _rg.angularVelocity = transform.right * _rotationSpeed;

        Destroy(gameObject, _lifetime);
    }

    public void SetVariables(GameObject caster, int damage, float hitForce, float speed, float rotationSpeed, Vector3 targetPos, float lifetime)
    {
        _caster = caster;
        _damage = damage;
        _hitForce = hitForce;
        _speed = speed;
        _rotationSpeed = rotationSpeed;
        _target = targetPos;
    }

    void OnTriggerEnter(Collider col)
    {
        if (GameDictionary.AreEnemies(_caster.tag, col.gameObject.tag))
        {
            Vector3 forceDirection = col.transform.position - transform.position;
            forceDirection.y = 0;
            forceDirection.Normalize();

            col.GetComponent<LivingEntity>().DecreaseHealth(_damage);
            col.gameObject.GetComponent<RigidbodyWrapper>().AddExternalForce(forceDirection * _hitForce);

            GameObject go = Instantiate(_hitVisualEffect);
            go.transform.position = transform.position;
            go.transform.LookAt(col.transform.position);

            Destroy(go, 3f);
            Destroy(gameObject);
        }

        if(col.gameObject.layer == LayerMask.GetMask("Wall"))
        {
            Destroy(gameObject);
        }
    }

}
