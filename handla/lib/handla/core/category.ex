defmodule Handla.Core.Category do
  defstruct ~w[name short ordinal]a

  def new(name, short, ordinal) do
    %__MODULE__{
      name: name,
      short: short,
      ordinal: ordinal
    }
  end
end
