using UnityEngine;

public class MobAttackPoint : MonoBehaviour {

    public GameObject parentEntity;

	void OnTriggerEnter(Collider col)
    {
        parentEntity.GetComponent<MobBehaviour>().OnAttackHit(col);
    }

    void OnTriggerStay(Collider col)
    {
        parentEntity.GetComponent<MobBehaviour>().OnAttackHit(col);
    }
}
