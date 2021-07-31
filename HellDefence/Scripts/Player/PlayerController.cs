using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private PlayerNumber _playerNumber;
    [SerializeField] GameObject _pointToCastToIndex;
    [SerializeField] AudioClip _deathSound;

    private RigidbodyWrapper _rgw;
    private PlayerAnimation _playerAnimation;
    private PlayerSpell _playerSpell;
    private PlayerCooldown _playerCooldown;
    private LivingEntity _livingEntity;
    private AudioSource _audioSource;

    private bool _isDead;

    private string _playerNo;

    void Start()
    {
        _rgw = GetComponent<RigidbodyWrapper>();
        _playerAnimation = GetComponent<PlayerAnimation>();
        _playerSpell = GetComponent<PlayerSpell>();
        _playerCooldown = GetComponent<PlayerCooldown>();
        _livingEntity = GetComponent<LivingEntity>();
        _audioSource = GetComponent<AudioSource>();

        _pointToCastToIndex = Instantiate(_pointToCastToIndex) as GameObject;
        _pointToCastToIndex.SetActive(false);

        _playerNo = _playerNumber.ToString();
    }

    void Update()
    {
        if (_isDead) { return; }

        // Take care of the mouse / move - spellcast
        Vector3 direction = Vector3.zero;
        SpellName spellPressed = SpellName.None;

        // Movement
        if (Input.GetButton("Vertical_" + _playerNo))
        {
            direction.z = Input.GetAxis("Vertical_" + _playerNo);
        }
        if (Input.GetButton("Horizontal_" + _playerNo))
        {
            direction.x = Input.GetAxis("Horizontal_" + _playerNo);
        }

        //Spell Choice
        if (Input.GetButtonDown("Fireball_" + _playerNo))
        {
            spellPressed = SpellName.Fireball;
        }
        if (Input.GetButtonDown("PlasmaField_" + _playerNo))
        {
            spellPressed = SpellName.PlasmaField;
        }
        if (Input.GetButtonDown("Teleport_" + _playerNo))
        {
            spellPressed = SpellName.Teleport;
        }
        if (Input.GetButtonDown("BulletStorm_" + _playerNo))
        {
            spellPressed = SpellName.BulletStorm;
        }
        if (Input.GetButtonDown("SpecialSpell_" + _playerNo) && _playerSpell.specialSpell != SpellName.None)
        {
            spellPressed = _playerSpell.specialSpell;
        }

        if (_playerSpell.selectedSpell == SpellName.None && !_playerSpell.spellOnCast)
        {
            _rgw.direction = direction;

            if (_rgw.HasDirection())
            {
                _playerAnimation.SetIsMoving(true);
            }
            else
            {
                _playerAnimation.SetIsMoving(false);
            }
        }
        else
        {
            _rgw.direction = Vector3.zero;
            _playerAnimation.SetIsMoving(false);
        }

        if(_playerSpell.selectedSpell != SpellName.None && !_playerSpell.spellOnCast)
        {
            UpdateCastPoint(direction, GameDictionary.GetMinSpellCastDistance(_playerSpell.selectedSpell),
                                        GameDictionary.GetMaxSpellCastDistance(_playerSpell.selectedSpell));
        }

        foreach (SpellName spellName in _playerSpell.GetPlayerSpells(true))
        {
            if (spellName == spellPressed)
            {
                if (_playerSpell.selectedSpell == SpellName.None && !_playerSpell.spellOnCast)
                {
                    if (GameDictionary.GetSpellType(spellName) == SpellType.InstantCast && _playerCooldown.HasCooldown(spellName))
                    {
                        _playerSpell.CastSpell(spellName);
                        _playerAnimation.SetIsMoving(false);
                    }
                    else if (GameDictionary.GetSpellType(spellName) == SpellType.NormalCast && _playerCooldown.HasCooldown(spellName))
                    {
                        _playerSpell.SelectSpell(spellName);
                        SetCastPointToDefaultPosition(GameDictionary.GetDefaultSpellCastDistance(spellName));
                    }
                }
                else if (!_playerSpell.spellOnCast && _playerSpell.selectedSpell == spellName) // and selectedSpell != SpellName.none
                {  
                    _playerSpell.CastSpell(_playerSpell.selectedSpell);
                    _playerSpell.SelectSpell(SpellName.None);
                    _playerAnimation.SetIsMoving(false);
                    HideCastPoint();
                }
            }
        }

        if (Input.GetButtonDown("SpellCancel_" + _playerNo))
        {
            _playerSpell.SelectSpell(SpellName.None);
            HideCastPoint();
        }

        if (!_isDead)
        {
            if (_livingEntity.isDead())
            {
                _isDead = true;
                _rgw.StopMoving();
                _rgw.EraseExternalForces();
                _audioSource.PlayOneShot(_deathSound);
                _playerAnimation.SetIsDead(true);
            }
        }
    }

    private void SetCastPointToDefaultPosition(float defaultDistance = 10f)
    {
        Vector3 newIndexPos = transform.position + transform.forward * defaultDistance + Vector3.up * .3f;
        newIndexPos.y = .2f;

        _pointToCastToIndex.SetActive(true);
        _pointToCastToIndex.transform.SetParent(transform);
        _pointToCastToIndex.transform.position = newIndexPos;
        _playerSpell.pointToCastTo = _pointToCastToIndex.transform.position;
    }

    private void UpdateCastPoint(Vector3 direction, float minDistance = 1f, float maxDistance = 40f)
    {
        Vector3 moveDelta = (_pointToCastToIndex.transform.position - transform.position).normalized * direction.z * Time.deltaTime * 70;
        moveDelta.y = .2f - _pointToCastToIndex.transform.position.y;

        if (Vector3.Distance(transform.position, _pointToCastToIndex.transform.position + moveDelta) < maxDistance &&
            Vector3.Distance(transform.position, _pointToCastToIndex.transform.position + moveDelta) > minDistance)
        {
            _pointToCastToIndex.transform.Translate(moveDelta, Space.World);
        }

        _pointToCastToIndex.transform.RotateAround(transform.position, Vector3.up, direction.x * Time.deltaTime * 150);

        _playerSpell.pointToCastTo = _pointToCastToIndex.transform.position;
    }

    private void HideCastPoint()
    {
        _pointToCastToIndex.SetActive(false);
    }
}


