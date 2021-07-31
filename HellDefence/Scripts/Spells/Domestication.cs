using UnityEngine;

public class Domestication : Spell {

    void Awake()
    {
        transform.position = caster.transform.position;
    }

	void Start () {

        Collider[] hitColliders =
                Physics.OverlapSphere(transform.position, 60f, LayerMask.GetMask("Mob"));

        GameObject target = null;
        float distance = Mathf.Infinity;

        foreach(Collider hitCol in hitColliders){
            if (hitCol.gameObject.GetComponent<MobBehaviour>())
            {
                if(Vector3.Distance(transform.position, hitCol.transform.position) < distance)
                {
                    target = hitCol.gameObject;
                    distance = Vector3.Distance(transform.position, hitCol.transform.position);
                }
            }
        }

        if (target != null)
        {
            target.GetComponent<MobBehaviour>().MakeItPlayerPet(Mathf.Infinity);
            target.GetComponent<LivingEntity>().maxHealth += 100;
            target.GetComponent<LivingEntity>().IncreaseHealth(100);
        }

        Destroy(gameObject);
    }

}
