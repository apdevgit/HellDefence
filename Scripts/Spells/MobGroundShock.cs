using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class MobGroundShock : Spell {

    [SerializeField] private int _damage = 10;
    [SerializeField] private float _force = 15f;
    [SerializeField] private float _lifetime = 1f;

    private List<SphereCollider> _triggers;

    void Awake()
    {
        _triggers = new List<SphereCollider>();
        FindAndInitializeTriggers(transform);
    }

    void Start()
    {
        StartCoroutine(DisableTriggersInTime(_lifetime));
        Destroy(gameObject, _lifetime + .5f);
    }

    private void FindAndInitializeTriggers(Transform current)
    {
        if(current.gameObject.name == "Trigger")
        {
            current.gameObject.GetComponent<GroundShockTrigger>().SetVariables(caster, _damage, _force);
            _triggers.Add(current.GetComponent<SphereCollider>());
            return;
        }

        int childNum = current.childCount;

        for(int i = 0; i <childNum; i++)
        {
            FindAndInitializeTriggers(current.GetChild(i));
        }
    }

    private IEnumerator DisableTriggersInTime(float time)
    {
        yield return new WaitForSeconds(time);

        foreach( SphereCollider col in _triggers)
        {
            if (col != null)
            {
                col.enabled = false;
            }
        }
    }
}
