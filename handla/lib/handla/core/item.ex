defmodule Handla.Core.Item do
  defstruct ~w[text category comment checked timestamp]a

  def new(text, category, comment \\ "", checked \\ true) do
    %__MODULE__{
      text: text,
      category: category,
      comment: comment,
      checked: checked,
      timestamp: DateTime.utc_now
    }
  end

  defp edit(item, new_text \\ nil, new_category \\ nil, new_comment \\ nil, new_checked \\ nil) do
    %__MODULE__{
      text:     (if new_text == nil,     do: item.text,     else: new_text),
      category: (if new_category == nil, do: item.category, else: new_category),
      comment:  (if new_comment == nil,  do: item.comment,  else: new_comment),
      checked:  (if new_checked == nil,  do: item.checked,  else: new_checked),
      timestamp: DateTime.utc_now
    }
  end

  def change_text(item, new_text) do
    edit(item, new_text)
  end

  def change_category(item, new_category) do
    edit(item, nil, new_category)
  end

  def change_comment(item, new_comment) do
    edit(item, nil, nil, new_comment)
  end

  def remove_comment(item) do
    edit(item, nil, nil, "")
  end

  def check(item) do
    edit(item, nil, nil, nil, true)
  end

  def uncheck(item) do
    edit(item, nil, nil, nil, false)
  end
end
