using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Drop : MonoBehaviour {

    [SerializeField] private List<GameObject> _drops;
    [SerializeField] private float _dropChance = .2f;

	public void TryToDrop()
    {
        if (Random.Range(1, 100) <= _dropChance * 100)
        {
            DropItem();
        }
    }

    private void DropItem()
    {
        int randomItemIndex = Random.Range(0, _drops.Count - 1);
        Vector3 position = transform.position;
        position += Vector3.up * 6;

        Instantiate(_drops[randomItemIndex], position, Quaternion.identity);
    }
}
