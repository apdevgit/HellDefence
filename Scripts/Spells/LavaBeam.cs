using UnityEngine;
using System.Collections;

public class LavaBeam : Spell {

    [SerializeField] private Transform _lineInbetween;

    [SerializeField] private int _damage = 4;
    [SerializeField] private float _damageFrequency = 8f;
    [SerializeField] private float _lifetime = 4.6f;

    private CapsuleCollider _damageCollider;

    private Stats _casterStats;

    private bool _alive = true;

    private float _maxBeamLength = 90f;
    private float _beamLength = 0;
    private float _distanceFromEndPoint;

    private float _beamSpeed = 30f;

    private bool _isApplyDamageFrame;

    void Awake()
    {
        _damageCollider = GetComponent<CapsuleCollider>();
        _distanceFromEndPoint = _maxBeamLength;

        transform.position = caster.position + caster.forward + Vector3.up * 2;
        transform.rotation = caster.rotation;

        _casterStats = caster.gameObject.GetComponent<Stats>();

        if (_casterStats != null)
        {
            _damage = (int)((_damage + _casterStats.damageConstant) * (_casterStats.damageQuota + 1));
        }
    }

	void Start () {
        StartCoroutine(ManageAndDestroy(_lifetime));
        StartCoroutine(ManageApplyDamageFrame());
    }
	
	void Update () {
        if (_alive)
        {
            FindSpellLengthByRaycast();
            UpdateBeamSize();
        }
    }

    private void FindSpellLengthByRaycast()
    {
        Ray ray = new Ray(transform.position + Vector3.up, transform.forward);
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit, _maxBeamLength, LayerMask.GetMask("Wall")))
        {
            _distanceFromEndPoint = Vector3.Distance(transform.position + Vector3.up, hit.point);
        }
    }

    private void UpdateBeamSize()
    {
        float newBeamLengthDelta = Mathf.Lerp(0, _maxBeamLength, Time.deltaTime / 3f);
        _beamLength = Mathf.Clamp(_beamLength + newBeamLengthDelta, 0, _distanceFromEndPoint);
        _lineInbetween.GetComponent<LineRenderer>().SetPosition(1, new Vector3(0, 0, _beamLength));
        _lineInbetween.GetComponent<Renderer>().material.mainTextureScale = new Vector2( _beamLength/10f, 1);

        Vector3 newColliderCenter = _damageCollider.center;
        newColliderCenter.z = _beamLength / 2;
        _damageCollider.center = newColliderCenter;

        _damageCollider.height = _beamLength;
        
    }

    private IEnumerator ManageApplyDamageFrame()
    {
        while (_alive)
        {
            yield return new WaitForSeconds(1 / _damageFrequency);

            _isApplyDamageFrame = true;
            yield return null;
            _isApplyDamageFrame = false;
        }
    }

    private IEnumerator ManageAndDestroy(float delay)
    {
        yield return new WaitForSeconds(delay);
        _alive = false;

        LineRenderer lr = _lineInbetween.GetComponent<LineRenderer>();

        float timeCounter = 0;
        float lineStartSize = 1.4f; // value known from the inspector

        while (timeCounter < .8f)
        {
            lr.SetWidth(Mathf.Lerp(lineStartSize, 0, timeCounter / .8f), Mathf.Lerp(lineStartSize, 0, timeCounter / .8f));
            timeCounter += Time.deltaTime;
            yield return null;
        }
        
        Destroy(gameObject);
    }

    void OnTriggerStay(Collider col)
    {
        if (!_isApplyDamageFrame) { return; }

        LivingEntity lv = col.gameObject.GetComponent<LivingEntity>();

        if(lv != null && caster != null)
        {
            if (GameDictionary.AreEnemies(caster.tag, col.gameObject.tag))
            {
                lv.DecreaseHealth(_damage);
            }
        }
    }

}
