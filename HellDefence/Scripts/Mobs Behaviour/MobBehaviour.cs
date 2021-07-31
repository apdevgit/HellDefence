using UnityEngine;
using System.Collections;

enum AIState
{
    Idle,
    Roaming,
    Chasing,
    Attacking,
    Resting,
    Dead
}

public class MobBehaviour : MonoBehaviour {

    // debug
    [SerializeField]
    private GameObject _moveIndex;

    private RigidbodyWrapper _rgw;
    private Animator _animator;
    private LivingEntity _livingEntity;
    private Throw _throw;
    private Cast _cast;
    private Drop _drop;
    private AudioSource _audioSource;

    private GameObject _playerPetVisualEffectPrefab;
    private GameObject _playerPetVisualEffect;

    [SerializeField] private GameObject _hitVisualEffect;
    private Transform _mobAttackPoint;

    private AIState _state;
    private AIState _previousState;

    [SerializeField] AnimationClip _attackAnimation;
    [SerializeField] float _attackAnimMultiplier = 1f;
    [SerializeField] bool _walkAnimDuringRotation;

    [Header("Audio Configuration")]
    [SerializeField] private bool _makesSoundOnAttack;
    [SerializeField] private float _attackSoundDelay = 0;
    [SerializeField] private AudioClip[] _attackSounds;
    [SerializeField] private AudioClip _deathSound;

    [Header("Attack Configuration")]
    [SerializeField] private int _damage = 11;
    [SerializeField] private float _hitForce = 200f;

    [SerializeField] private float _chasingRadius = 15f;

    // Roaming State
    private bool _commandedDestination;
    private IEnumerator SetRandDestCoroutine;
    //

    // Attacking State
    [SerializeField] private float _attackingDistance = 6f;
    [SerializeField] private float _attackFrequency = 4f;
    [SerializeField] private float _restTimeAfterAttack = 2f;
    [SerializeField] private float _attackPredictionOffset = 15f;
    [SerializeField] private float _attackFieldOfView = 15f; // degrees
    private bool _canAttack;
    private bool _isOnAttack;
    //

    // Resting State
    private bool _isResting;
    //

    // Dead state
    [SerializeField] private float _disappearTimeAfterDeath = 4f;
    //

    [Header("Ranged Attack Settings")]
    [SerializeField] private bool _attackIsRanged;
    [SerializeField] private float _throwingObjectSpeed = 10f;
    [SerializeField] private float _throwingObjectRotationSpeed = 5f;
    [SerializeField] private float _throwingObjectLifetime = 4f;
    [SerializeField] private float _momentToThrowQuota = 1f;

    [Header("Caster Attack Settings")]
    [SerializeField] private bool _attackIsSpellCast;
    [SerializeField] private float _momentToCastQuota = 1f;

    private Transform _target;
    private bool _hasJustHitEnemy;

    private AIState state
    {
        get { return _state; }
        set
        {
            _state = value;
        }
    }

    void Awake()
    {
        _rgw = GetComponent<RigidbodyWrapper>();
        _animator = GetComponent<Animator>();
        _animator.SetFloat("AttackAnimMultiplier", _attackAnimMultiplier);
        _livingEntity = GetComponent<LivingEntity>();
        _drop = GetComponent<Drop>();
        _audioSource = GetComponent<AudioSource>();

        _playerPetVisualEffectPrefab = Resources.Load("star6") as GameObject;

        if (_attackIsRanged)
        {
            _throw = GetComponent<Throw>();
        }
        else if(_attackIsSpellCast)
        {
            _cast = GetComponent<Cast>();
        }

        _target = null;

        float attackTime =  _attackAnimation.length / _attackAnimMultiplier;
        if (_attackFrequency < attackTime)
        {
            _attackFrequency = attackTime;
        }

        _canAttack = true;
        _isResting = false;
        _isOnAttack = false;
        state = AIState.Idle;
        InitializeAttackPoint(transform);

    }
	
    void Start()
    {
        _animator.SetFloat("AttackAnimMultiplier", _attackAnimMultiplier);
    }

	void Update () {
	    
        if(state == AIState.Idle)
        {
            if(_previousState != _state)
            {
                _animator.SetBool("Walk", false);
                _rgw.StopMoving();
            }

            ChangeState();
        }
        else if(state == AIState.Roaming)
        {
            if(_previousState != AIState.Roaming)
            {
                _animator.SetBool("Walk", true);
            }

            // if there is wall on the way, find a new way
            if (IsGoingToHitTheWall())
            {
                if (FacesToTheDestination() || IsGoingToHitTheWall(_rgw.destination))
                {
                    if (SetRandDestCoroutine != null)
                    {
                        StopCoroutine(SetRandDestCoroutine);
                    }

                    EscapeAfterWallFound();
                }
            }

            // start/keep roaming
            if (!_rgw.HasDestination() && !_commandedDestination)
            {
                SetRandDestCoroutine = SetRandomDestination(Random.Range(1f, 2f));
                StartCoroutine(SetRandDestCoroutine);
            }

            if (ChangeState())
            {
                _commandedDestination = false;
                if (SetRandDestCoroutine != null)
                {
                    StopCoroutine(SetRandDestCoroutine);
                }
            }

        }
        else if(state == AIState.Chasing)
        {
            if(_target == null)
            {
                ChangeState();
                return;
            }

            Vector3 playerPos = _target.position;
            Vector3 attackDestination = playerPos + 
                _target.GetComponent<Rigidbody>().velocity * _attackPredictionOffset * Time.deltaTime;

            playerPos.y = transform.position.y;
            attackDestination.y = transform.position.y;

            // start/keep chasing
            _rgw.destination = new Vector3(playerPos.x, transform.position.y, playerPos.z);

            if(Vector3.Distance(playerPos, new Vector3(transform.position.x, playerPos.y, transform.position.z)) > _attackingDistance)
            {
                _animator.SetBool("Walk", true);
                if(_rgw.onlyRotate)
                {
                    _rgw.onlyRotate = false;
                }
            } 
            else if(!_rgw.onlyRotate)//if it has reached attacking distance but the angle is not right and onlyRotate is false:
            {
                _rgw.onlyRotate = true;
                if (_walkAnimDuringRotation)
                {
                    _animator.SetBool("Walk", false);
                }
            }

            ChangeState();
        }
        else if(state == AIState.Resting)
        {

            if (_previousState != AIState.Resting)
            {
                _animator.SetBool("Walk", false);
                _rgw.StopMoving();
            }

            ChangeState();
        }
        else if (state == AIState.Attacking)
        {
            if(_previousState == AIState.Chasing || _previousState == AIState.Roaming)
            {
                _animator.SetBool("Walk", false);
            }

            if (IsAbleToAttack() && !_isOnAttack)
            {
                Vector3 enemiePos = _target.position;
                Vector3 attackDestination = enemiePos +
                    _target.GetComponent<Rigidbody>().velocity * _attackPredictionOffset * Time.deltaTime;
                attackDestination.y = transform.position.y;

                // if the enemie is walking towards you and his pos + velocity goes behind you, fix it.
                if (Vector3.Angle(_target.position - transform.position, attackDestination - transform.position) >
                        Vector3.Angle(transform.position - _target.position, attackDestination - transform.position))
                {
                    attackDestination = enemiePos;
                }

                _rgw.LookAtOnCertainTime(attackDestination, _attackAnimation.length / _attackAnimMultiplier);

                _animator.SetBool("Attack", true);
                _canAttack = false;
                _isOnAttack = true;
                _rgw.StopMoving();

                if (_attackIsRanged) {
                    float atTime = (_attackAnimation.length / _attackAnimMultiplier) * _momentToThrowQuota;
                    StartCoroutine(ThrowAttackInTime(atTime));
                }
                else if (_attackIsSpellCast)
                {
                    float atTime = (_attackAnimation.length / _attackAnimMultiplier) * _momentToCastQuota;
                    StartCoroutine(CastSpellInTime(atTime));
                }

                if(_makesSoundOnAttack && _audioSource != null)
                {
                    StartCoroutine(PlaySoundInTime(_attackSounds[Random.Range(0, _attackSounds.Length)], _attackSoundDelay));

                }

                StartCoroutine(ManageAfterAttack());
            }

            ChangeState();
        }
        else if(state == AIState.Dead)
        {
            if(_previousState != AIState.Dead)
            {
                _animator.SetBool("Die", true);
                _rgw.StopMoving();

                if(_drop != null)
                {
                    _drop.TryToDrop();
                }

                if (_deathSound != null)
                {
                    _audioSource.PlayOneShot(_deathSound);
                }

                gameObject.layer = LayerMask.NameToLayer("Dead");
                Destroy(gameObject, _disappearTimeAfterDeath);
            }

            _previousState = AIState.Dead;
        }
	}

    // Checks if state must change. If it must change, then change it and return true. Else return false.
    private bool ChangeState()
    {
        AIState stateToChangeTo = state;

        if(_target == null)
        {
            _target = FindTargetInRadius();
        }

        if (_livingEntity.isDead())
        {
            stateToChangeTo = AIState.Dead;
        }
        else if (_isResting)
        {
            stateToChangeTo = AIState.Resting;
        }
        else if (IsAbleToAttack())
        {
            stateToChangeTo = AIState.Attacking;
        }
        else if (IsAbleToChase())
        {
            stateToChangeTo = AIState.Chasing;
        }
        else if (IsAbleToRoam())
        {
            stateToChangeTo = AIState.Roaming;
        }
        else
        {
            stateToChangeTo = AIState.Idle;
        }

        if(_state != _previousState)
        {
            _previousState = state;
        }

        if(stateToChangeTo != state)
        {
            state = stateToChangeTo;
            if(_previousState == AIState.Chasing || _previousState == AIState.Attacking)
            {
                _rgw.onlyRotate = false;
            }
            return true;
        }

        return false;
    }

    private bool IsAbleToAttack()
    {
        if (_target != null)
        {
            Vector3 playerPos = _target.position;
            playerPos.y = transform.position.y;

            if (Vector3.Distance(playerPos, transform.position) <= _attackingDistance
                && Vector3.Angle(transform.forward, playerPos - transform.position) < _attackFieldOfView
                && _canAttack && !_isResting && !ThereIsWallBetween(transform.position, playerPos)
                && _target.GetComponent<LivingEntity>().isAlive()
                && GameDictionary.AreEnemies(gameObject.tag, _target.tag)
                || _isOnAttack)
            {
                return true;
            }
        }

        return false;
    }

    private bool IsAbleToChase()
    {
        if (_target != null)
        {
            Vector3 targetPos = _target.position;
            targetPos.y = transform.position.y;

            if (Vector3.Distance(targetPos, transform.position) > _chasingRadius
                || ThereIsWallBetween(transform.position, targetPos)
                || _target.GetComponent<LivingEntity>().isDead()
                || !GameDictionary.AreEnemies(gameObject.tag, _target.tag))
            {
                _target = null;
                return false;
            }
            else if ( !_isResting && !_isOnAttack)
            {
                return true;
            }
        }

        return false;
    }

    private bool IsAbleToRoam()
    {
        if (!_isResting && !_isOnAttack)
        {
            return true;
        }

        return false;
    }

    private IEnumerator ThrowAttackInTime(float time)
    {
        yield return new WaitForSeconds(time);

        Vector3 attackPos = _target.position + _target.GetComponent<Rigidbody>().velocity * _attackPredictionOffset * Time.deltaTime;
        Vector3 attackDestination = _target.position +
            _target.GetComponent<Rigidbody>().velocity * _attackPredictionOffset * Time.deltaTime;
        attackDestination.y = transform.position.y;

        if (Vector3.Angle(_target.position - transform.position, attackDestination - transform.position) >
                            Vector3.Angle(transform.position - _target.position, attackDestination - transform.position))
        {
            attackPos = _target.position + transform.forward;
        }

        _throw.ThrowObject(_damage, _hitForce, _throwingObjectSpeed, _throwingObjectRotationSpeed, attackPos, _throwingObjectLifetime);
    }

    private IEnumerator CastSpellInTime(float time)
    {
        yield return new WaitForSeconds(time);

        _cast.CastSpell();
    }

    private Transform FindTargetInRadius()
    {
        Transform target = null;

        Collider[] hitColliders =
                Physics.OverlapSphere(transform.position, _chasingRadius);

        foreach (Collider hitCollider in hitColliders)
        {
            if (GameDictionary.AreEnemies(gameObject.tag, hitCollider.gameObject.tag))
            {
                if(target == null)
                {
                    target = hitCollider.transform;
                }
                else
                {
                    if (Vector3.Distance(transform.position, hitCollider.transform.position) < Vector3.Distance(transform.position, target.position))
                    {
                        target = hitCollider.transform;
                    }
                }
            }    
        }

        return target;
    }

    private IEnumerator SetRandomDestination(float delay)
    {
        _commandedDestination = true;
        _animator.SetBool("Walk", false);
        float newDestinationangle = Random.Range(1, 360);
        
        transform.Rotate(Vector3.up, newDestinationangle);
        Vector3 newDestination = transform.position + transform.forward * 20;
        transform.Rotate(Vector3.up, -newDestinationangle);

        //Instantiate(_moveIndex, newDestination, Quaternion.identity);

        yield return new WaitForSeconds(delay);
        _animator.SetBool("Walk", true);
        _commandedDestination = false;
        _rgw.destination = newDestination;
    }

    private void EscapeAfterWallFound()
    {
        float newDestinationAngle;
        Vector3 dir;

        for(int i = 0; i < 20; i++)
        {
            newDestinationAngle = Random.Range(30, 330);
            
            dir = Quaternion.Euler(0, newDestinationAngle, 0) * transform.forward; // rotate the vector direction

            if (!Physics.Raycast(transform.position, dir, 10f, LayerMask.GetMask("Wall")))
            {
                _animator.SetBool("Walk", true);
                _commandedDestination = false;
                _rgw.destination = transform.position + dir.normalized * (20 + Random.Range(-10, 10));
                return;
            }
        }

        _animator.SetBool("Walk", false);
    }

    private bool IsGoingToHitTheWall(float distance = 4f)
    {
        Vector3 fwd = transform.TransformDirection(Vector3.forward);
        Vector3 fwdLeft = Quaternion.Euler(0, -30, 0) * fwd;
        Vector3 fwdRight = Quaternion.Euler(0, 30, 0) * fwd;

        Debug.DrawLine(transform.position + Vector3.up, transform.position + Vector3.up + fwd * distance, Color.red);
        Debug.DrawLine(transform.position + Vector3.up, transform.position + Vector3.up + fwdLeft * distance, Color.red);
        Debug.DrawLine(transform.position + Vector3.up, transform.position + Vector3.up + fwdRight * distance, Color.red);

        if (Physics.Raycast(transform.position + Vector3.up, fwd, distance, LayerMask.GetMask("Wall")) ||
            Physics.Raycast(transform.position + Vector3.up, fwdLeft, distance, LayerMask.GetMask("Wall")) ||
            Physics.Raycast(transform.position + Vector3.up, fwdRight, distance, LayerMask.GetMask("Wall")) )
        {
            return true;
        }

        return false;
    }

    private bool IsGoingToHitTheWall(Vector3 destinationPoint, float distance = 4f)
    {
        Vector3 toDest = transform.TransformDirection(destinationPoint);
        Debug.DrawLine(transform.position + Vector3.up, transform.position + Vector3.up + toDest.normalized * distance, Color.cyan);
        if (Physics.Raycast(transform.position + Vector3.up, toDest, distance, LayerMask.GetMask("Wall")))
        {
            return true;
        }

        return false;
    }

    private bool ThereIsWallBetween(Vector3 start, Vector3 target)
    {
        Vector3 toDest = target - start;
        float distance = toDest.magnitude;

        if (Physics.Raycast(start, toDest, distance, LayerMask.GetMask("Wall")))
        {
            return true;
        }

        return false;
    }

    private bool FacesToTheDestination()
    {
        Vector3 fwd = transform.TransformDirection(Vector3.forward);
        Vector3 toDest = _rgw.destination - transform.position;
        toDest.y = 0;

        Debug.DrawLine(transform.position + Vector3.up, transform.position + Vector3.up + toDest.normalized * 5, Color.cyan);
        Debug.DrawLine(transform.position + Vector3.up, _rgw.destination +Vector3.up , Color.blue);

        if (Mathf.Abs(Vector3.Angle(fwd, toDest)) < 30)
        {
            return true;
        }

        return false;
    }

    private IEnumerator ManageAfterAttack()
    {
        StartCoroutine(RefreshAttack());
        
        yield return new WaitForSeconds(_attackAnimation.length / _attackAnimMultiplier);
        _isOnAttack = false;
        _animator.SetBool("Attack", false);

        if (_restTimeAfterAttack > 0)
        {
            StartCoroutine(RestForSeconds(_restTimeAfterAttack));
        }
    }

    private IEnumerator RefreshAttack()
    {
        yield return new WaitForSeconds(_attackFrequency);
        _hasJustHitEnemy = false;
        _canAttack = true;
    }

    private IEnumerator RestForSeconds(float seconds)
    {
        _isResting = true;
        _animator.SetBool("Walk", false);
        yield return new WaitForSeconds(seconds);

        _isResting = false;
    }

    public void OnAttackHit(Collider col)
    {
        if( GameDictionary.AreEnemies(gameObject.tag, col.gameObject.tag) && _animator.GetCurrentAnimatorStateInfo(0).IsName("Attack") && !_hasJustHitEnemy)
        {
            Vector3 forceDirection = col.transform.position - transform.position;
            forceDirection.y = 0;

            col.GetComponent<LivingEntity>().DecreaseHealth(_damage);
            col.gameObject.GetComponent<RigidbodyWrapper>().AddExternalForce(forceDirection.normalized * _hitForce);
            _hasJustHitEnemy = true;

            GameObject go = Instantiate(_hitVisualEffect);
            go.transform.position = _mobAttackPoint.position;
            go.transform.SetParent(col.transform);
            Destroy(go, 3f);
        }
    }

    private void InitializeAttackPoint(Transform transform)
    {
        foreach(Transform tr in transform)
        {
            if(tr.name == "MobAttackPoint")
            {
                _mobAttackPoint = tr;
                tr.gameObject.AddComponent<MobAttackPoint>().parentEntity = this.gameObject;
                return;
            }
            else
            {
                InitializeAttackPoint(tr);
            }
        }
    }

    public void MakeItPlayerPet(float seconds)
    {
        StartCoroutine(MakeItPlayerPetCo(seconds));
    }

    private IEnumerator MakeItPlayerPetCo(float seconds)
    {
        state = AIState.Idle;
        ChangeMaskRecursively(transform, LayerMask.NameToLayer("PlayerPet"));
        gameObject.tag = "PlayerPet";

        _playerPetVisualEffect = Instantiate(_playerPetVisualEffectPrefab) as GameObject;
        _playerPetVisualEffect.transform.SetParent(transform);
        _playerPetVisualEffect.transform.localScale = Vector3.one;
        _playerPetVisualEffect.transform.localPosition = Vector3.zero;
        Destroy(_playerPetVisualEffect, seconds);

        yield return new WaitForSeconds(seconds);

        MakeItMob();
    }

    public void MakeItMob()
    {
        state = AIState.Idle;
        ChangeMaskRecursively(transform, LayerMask.NameToLayer("Mob"));
        gameObject.tag = "Mob";

        if(_playerPetVisualEffect != null)
        {
            Destroy(_playerPetVisualEffect);
        }

    }

    private IEnumerator PlaySoundInTime(AudioClip audioClip, float time)
    {
        yield return new WaitForSeconds(time);

        _audioSource.PlayOneShot(audioClip);
    }

    public void SetDestination(Vector3 destination)
    {
        state = AIState.Roaming;
        _rgw.destination = destination;
    }

    private void ChangeMaskRecursively(Transform tr, LayerMask lm)
    {
        foreach (Transform child in tr)
        {
            child.gameObject.layer = lm;
            ChangeMaskRecursively(child, lm);
        }
    }
}
