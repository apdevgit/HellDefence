using UnityEngine;
using System.Collections;

[RequireComponent(typeof(Rigidbody))]
public class RigidbodyWrapper : MonoBehaviour {

    private enum Mode
    {
        BasedOnDestination,
        BasedOnDirection,
        SimpleObject
    }

    [SerializeField] private Mode _mode = Mode.SimpleObject;
    [SerializeField] private float _rotationSpeed = 5;
    [SerializeField] private float _friction = 5;
    [SerializeField] private float _speed = 5;
    [SerializeField] private float _mass = 1;
    [SerializeField] private bool _isLivingThing = false;

    private Rigidbody _rg;

    private Vector3 _externalForces;
    private Vector3 _destination;
    private Vector3 _direction;

    private bool _hasDestination;
    private bool _hasDirection;
    private bool _isFrozenXZ;

    private bool _onlyRotate;

    public bool onlyRotate
    {
        get { return _onlyRotate; }
        set { _onlyRotate = value; }
    }

    public float mass
    {
        get { return _mass; }
        set { _mass = value; }
    }

    public float speed
    {
        get { return _speed; }
        set { _speed = value; }
    }

    public Vector3 destination
    {
        get { return _destination; }
        set
        {
            if (_mode == Mode.BasedOnDestination)
            {
                _destination = value;
                _hasDestination = true;
            }
            if (value == Vector3.zero && _hasDestination)
            {
                _hasDestination = false;
            }
        }
    }

    public Vector3 direction
    {
        get { return _destination; }
        set
        {
            if (_mode == Mode.BasedOnDirection && value != Vector3.zero)
            {
                _direction = value;
                _hasDirection = true;
            }
            if(value == Vector3.zero && _hasDirection)
            {
                _hasDirection = false;
            }
        }
    }

    void Awake () {
        _rg = GetComponent<Rigidbody>();

        _externalForces = Vector3.zero;
        _destination = Vector3.zero;
        _direction = Vector3.zero;
        _rg.mass = _mass;
	}

    void FixedUpdate()
    {
        if (_isLivingThing)
        {
            FixRotation();
        }

        if(gameObject.tag == "Player")
        {
            //Debug.Log(_externalForces);
        }
        else
        {
            Debug.DrawLine(transform.position + Vector3.up, _destination + Vector3.up, Color.green);
        }

        ApplyFriction();
        
        if (_hasDestination && _mode == Mode.BasedOnDestination)
        {
            Vector3 moveDestination = _destination - transform.position;
            moveDestination.y = 0;
            
            // if distance to the destination is smaller than the next position, then stop
            if (moveDestination.magnitude < _speed * Time.fixedDeltaTime)
            {
                _hasDestination =  false;
            }
            else
            {
                moveDestination.Normalize();
                Vector3 movement;

                if (_onlyRotate)
                {
                    movement = Vector3.zero;
                }
                else
                {
                    movement = moveDestination * _speed;
                }

                _rg.velocity = movement +
                                _externalForces  +
                                new Vector3(0, Mathf.Min(_rg.velocity.y, 0), 0) + Physics.gravity * Time.fixedDeltaTime;

                Quaternion rotation = Quaternion.LookRotation(moveDestination);
                transform.rotation = Quaternion.Slerp(transform.rotation, rotation, Time.fixedDeltaTime * _rotationSpeed);
            }
        }
        else if (_hasDirection && _mode == Mode.BasedOnDirection)
        {
            Vector3 movement = transform.forward;

            if (_onlyRotate)
            {
                movement = Vector3.zero;
            }
            else
            {
                movement = movement * _speed;
            }

            _rg.velocity = movement +
                            _externalForces + 
                            new Vector3(0, Mathf.Min(_rg.velocity.y, 0), 0) + Physics.gravity * Time.fixedDeltaTime;

            Quaternion rotation = Quaternion.LookRotation(_direction);
            transform.rotation = Quaternion.Slerp(transform.rotation, rotation, Time.fixedDeltaTime * _rotationSpeed);
        }
        else
        {
            _rg.velocity = _externalForces / _rg.mass +
                            new Vector3(0, _rg.velocity.y, 0) + Physics.gravity * Time.deltaTime;
            _rg.angularVelocity = new Vector3(0, 0, 0);
        }
    }

    private bool mustMove()
    {
        if(_externalForces.x == 0 && _externalForces.z == 0 && _speed == 0)
        {
            return false;
        }
        return true;
    }

    private void ApplyFriction()
    {
        if (_externalForces.magnitude <= _friction * Time.fixedDeltaTime)
        {
            _externalForces = Vector3.zero;
        }
        else
        {
            Vector3 oppositeForce = -_externalForces.normalized * _friction * Time.fixedDeltaTime;
            _externalForces += oppositeForce;
        }
    }

    // Used for alive objects (Players, Mobs, etc.)
    private void FixRotation()
    {
        Vector3 curRotation = transform.eulerAngles;
        if (curRotation.x != 0)
        {
            curRotation.x = 0;
        }
        if (curRotation.z != 0)
        {
            curRotation.z = 0;
        }

        transform.rotation = Quaternion.Euler(curRotation);
    }

    public bool HasDestination()
    {
        return _hasDestination;
    }

    public bool HasDirection()
    {
        return _hasDirection;
    }

    public void AddExternalForce(Vector3 force)
    {
        _externalForces += (force) / (50 * _rg.mass);
    }

    public void StopMoving()
    {
        _hasDestination = false;
        _hasDirection = false;
    }

    public void LookAtOnCertainTime(Vector3 target, float time)
    {
        StartCoroutine(LookAtOnCertainTimeCo(target, time));
    }

    private IEnumerator LookAtOnCertainTimeCo(Vector3 target, float time)
    {
        Quaternion rotation = transform.rotation;
        Vector3 direction = target - transform.position;
        Quaternion to = Quaternion.LookRotation(direction);

        float timeCounter = 0;

        while(timeCounter < time)
        {
            transform.rotation = Quaternion.Lerp(rotation, to, timeCounter * 2 / time);
            timeCounter += Time.deltaTime;
            yield return null;
        }
    }
    
    public void EraseExternalForcesForTime(float time)
    {
        StartCoroutine(EraseExternalForcesForTimeCo(time));
    }

    private IEnumerator EraseExternalForcesForTimeCo(float time)
    {
        float timeCount = 0;
        
        while(timeCount < time)
        {
            EraseExternalForces();
            timeCount += Time.deltaTime;

            yield return new WaitForEndOfFrame();
        }
    }

    public void EraseExternalForces()
    {
        if (_externalForces != Vector3.zero)
        {
            _externalForces = Vector3.zero;
        }
    }

    void OnCollisionEnter(Collision col)
    {
        if (col.gameObject.layer == LayerMask.NameToLayer("Wall"))
        {
            _externalForces = Vector3.zero;

        }
    }
}
