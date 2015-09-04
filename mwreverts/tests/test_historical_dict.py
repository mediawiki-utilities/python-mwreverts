from nose.tools import eq_

from ..historical_dict import HistoricalDict


def test_historical_dict():
    d = HistoricalDict(3)

    assert "foo" not in d

    expectorate = d.insert("foo", "bar1")
    eq_(expectorate, None)
    assert "foo" in d
    eq_(d['foo'], "bar1")

    expectorate = d.insert("foo", "bar2")
    eq_(expectorate, None)
    assert "foo" in d
    eq_(d['foo'], "bar2")

    expectorate = d.insert("bar", "foo1")
    eq_(expectorate, None)
    assert "bar" in d
    eq_(d['bar'], "foo1")

    expectorate = d.insert("bar", "foo2")
    eq_(expectorate, ("foo", "bar1"))
    assert "bar" in d
    eq_(d['bar'], "foo2")
    eq_(d['foo'], "bar2")

    print(d.to_json())
    eq_(d, HistoricalDict(d.to_json()))
