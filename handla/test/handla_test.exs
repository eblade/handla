defmodule HandlaTest do
  use ExUnit.Case
  doctest Handla

  test "greets the world" do
    assert Handla.hello() == :world
  end
end
