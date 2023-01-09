defmodule ListTest do
  use ExUnit.Case
  use Builders

  test "items are sorted by category ordinal, then name" do
    sorted = List.sort(test_games(test_categories()))
    assert Enum.at(sorted.items, 0).text == "call of duty (a)"
  end
end
