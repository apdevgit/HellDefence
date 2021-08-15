using UnityEngine;
using System.Collections;

public class HealthKit : MonoBehaviour {

    private int _healValue = 20;
    private float _lifetime = 20f;
    private float _isPickableDelayTime = 1f;
    private bool _isPickable;

    [SerializeField] GameObject _effectVisual;
    private float _effectDuration = 3.5f;

    void Start()
    {
        StartCoroutine(MakeItPickableAfterDelay());
        Destroy(gameObject, _lifetime);
    }

    private IEnumerator MakeItPickableAfterDelay()
    {
        yield return new WaitForSeconds(_isPickableDelayTime);

        _isPickable = true;
    }

    void OnTriggerEnter(Collider col)
    {
        if (!_isPickable) { return; }
        
        if(col.tag == "Player")
        {
            col.GetComponent<LivingEntity>().IncreaseHealth(_healValue);
            GameObject visual = Instantiate(_effectVisual);
            visual.transform.SetParent(col.transform);
            visual.transform.localPosition = Vector3.zero - Vector3.up/2 ;
            Destroy(visual, _effectDuration);


            Destroy(gameObject);
        }
    }
}
